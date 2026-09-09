#!/usr/bin/env python3
"""Verify a cruise-data-transfer destination and optionally repair differences.

The checker loads a Cruise Data Transfer from OpenVDM, reuses the transfer
worker's exclude-list builder, compares source and destination sizes, and then
runs an exact ``rclone check --size-only``. If that check finds differences,
the operator may explicitly confirm a production-equivalent ``rclone sync``;
the script then verifies the result. This is intended for finalized cruises
whose Cruise Data Transfer uses sync semantics (equivalent to rsync
``--delete``), not copy semantics.

Usage::

    sudo -H /opt/openvdm/venv/bin/python \
        /opt/openvdm/utils/check_cruise_data_transfer.py FKt260806
    sudo -H /opt/openvdm/venv/bin/python \
        /opt/openvdm/utils/check_cruise_data_transfer.py FKt260806 \
        --transfer GoogleCloudSync
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.lib.connection_utils import (  # noqa: E402
    build_rclone_options,
    get_transfer_type,
)
from server.lib.openvdm import OpenVDM  # noqa: E402
from server.workers.run_cruise_data_transfer import OVDMGearmanWorker  # noqa: E402


def human_size(value):
    """Return a byte count in a compact human-readable form."""

    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if size < 1024 or unit == "PiB":
            return f"{size:,.2f} {unit}"
        size /= 1024

    return f"{size:,.2f} PiB"


def safe_filename(value):
    """Return *value* with characters unsafe for filenames replaced."""

    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def build_excludes(ovdm, cruise_id, transfer, warehouse, source):
    """Build exclusions using the production transfer worker implementation."""

    # Avoid OVDMGearmanWorker.__init__ because it connects to Gearman. The
    # exclude builder only needs these four attributes.
    worker = OVDMGearmanWorker.__new__(OVDMGearmanWorker)
    worker.ovdm = ovdm
    worker.cruise_id = cruise_id
    worker.cruise_data_transfer = transfer
    worker.shipboard_data_warehouse_config = warehouse
    worker.cruise_dir = source
    return worker.build_exclude_filterlist()


def write_excludes(path, excludes):
    """Write the exclude file in the same format as the transfer worker."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write("\n".join(excludes))
        file.write("\0")


def rclone_size(path, exclude_file):
    """Return rclone's JSON size result for *path*."""

    result = subprocess.run(
        ["rclone", "size", path, "--exclude-from", str(exclude_file), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def append_status(log_file, label, returncode):
    """Append a durable, timestamped command status to *log_file*."""

    completed_at = datetime.now(timezone.utc).isoformat()
    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"{completed_at} {label}_EXIT_STATUS={returncode}\n")


def run_check(source, destination, exclude_file, log_file):
    """Run an exact, read-only rclone comparison and return its exit status."""

    command = [
        "rclone",
        "check",
        source,
        destination,
        "--size-only",
        "--exclude-from",
        str(exclude_file),
        "--progress",
        "--log-file",
        str(log_file),
        "--log-level",
        "INFO",
    ]
    result = subprocess.run(command, check=False)
    append_status(log_file, "CHECK", result.returncode)
    return result.returncode


def resync_settings(ovdm, args):
    """Return current transfer flags, or an explanation of why sync is unsafe."""

    transfer = ovdm.get_cruise_data_transfer_by_name(args.transfer)
    if not transfer:
        return None, f"transfer no longer exists: {args.transfer}"

    copy_sync, flags = build_rclone_options(transfer, mode="real")
    if copy_sync != "sync":
        return None, "the saved transfer is configured for copy, not sync"

    current_cruise = ovdm.get_cruise_id()
    system_status = ovdm.get_system_status()
    if args.cruise_id == current_cruise and system_status == "On":
        return None, "this is the active cruise and OpenVDM is On"

    transfer_status = int(transfer.get("status", 0) or 0)
    if transfer_status in (1, 5, 6):
        names = {1: "Running", 5: "Stopping", 6: "Starting"}
        return None, f"{args.transfer} is {names[transfer_status]}"

    return flags, None


def sync_log_path(check_log_file):
    """Derive a distinct sync log path from a check log path."""

    suffix = ".check.log"
    if check_log_file.name.endswith(suffix):
        name = f"{check_log_file.name[:-len(suffix)]}.sync.log"
    else:
        name = f"{check_log_file.name}.sync.log"
    return check_log_file.with_name(name)


def offer_resync(ovdm, args, source, destination, exclude_file, log_file):
    """Offer a guarded sync after a failed check, then verify it again."""

    flags, blocker = resync_settings(ovdm, args)
    if blocker:
        print(f"Resync unavailable: {blocker}", file=sys.stderr)
        return 1

    print("\nWARNING: sync can delete destination-only objects.", file=sys.stderr)
    try:
        confirmation = input(
            f"Type {args.cruise_id} to synchronize the destination, "
            "or press Enter to cancel: "
        )
    except EOFError:
        confirmation = ""

    if confirmation != args.cruise_id:
        print("Resync cancelled; no data was changed")
        return 1

    # The check may take a long time and the confirmation may sit at the
    # prompt. Refresh the shared transfer state immediately before starting.
    flags, blocker = resync_settings(ovdm, args)
    if blocker:
        print(f"Resync refused after final safety check: {blocker}", file=sys.stderr)
        return 1

    sync_log_file = sync_log_path(log_file)
    sync_log_file.parent.mkdir(parents=True, exist_ok=True)
    sync_log_file.write_text("", encoding="utf-8")
    command = [
        "rclone",
        "sync",
        source,
        destination,
        *flags,
        "--exclude-from",
        str(exclude_file),
        "--log-file",
        str(sync_log_file),
        "--log-level",
        "INFO",
    ]
    print(f"Running sync; log: {sync_log_file}")
    result = subprocess.run(command, check=False)
    append_status(sync_log_file, "SYNC", result.returncode)
    if result.returncode != 0:
        print(
            f"FAIL: rclone sync exited with status {result.returncode}",
            file=sys.stderr,
        )
        return result.returncode

    print("Sync completed successfully; verifying again...")
    post_sync_status = run_check(source, destination, exclude_file, log_file)
    if post_sync_status == 0:
        print("PASS: post-sync verification found no differences")
    else:
        print(
            f"FAIL: post-sync check exited with status {post_sync_status}",
            file=sys.stderr,
        )
    return post_sync_status


def resolve_destination(transfer, cruise_id):
    """Resolve destinations directly addressable by rclone."""

    dest_dir = transfer["destDir"].rstrip("/")
    transfer_type = get_transfer_type(transfer["transferType"])

    if transfer_type != "local":
        raise ValueError(
            "This checker currently supports generic rclone remotes and local-directory "
            "Cruise Data Transfers, not SMB, rsync-server, or SSH configurations"
        )

    return f"{dest_dir}/{cruise_id}/"


def parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Verify a Cruise Data Transfer with its production excludes"
    )
    parser.add_argument("cruise_id", help="Cruise ID to verify, for example FKt260806")
    parser.add_argument(
        "--transfer",
        default="GoogleCloudSync",
        help="Cruise Data Transfer name (default: GoogleCloudSync)",
    )
    parser.add_argument(
        "--exclude-file",
        type=Path,
        help="Where to save the generated exclude list (default: /var/tmp/<cruise>-<transfer>.excludes)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Where to save rclone output and the final exit status (default: /var/tmp/<cruise>-<transfer>.check.log)",
    )
    parser.add_argument(
        "--excludes-only",
        action="store_true",
        help="Generate and display the exclude list without contacting the destination",
    )
    return parser.parse_args()


def main():
    """Generate exclusions and verify the configured destination."""

    args = parse_args()
    ovdm = OpenVDM()
    transfer = ovdm.get_cruise_data_transfer_by_name(args.transfer)
    if not transfer:
        print(f"Transfer not found: {args.transfer}", file=sys.stderr)
        return 2

    warehouse = ovdm.get_shipboard_data_warehouse_config()
    source = os.path.join(
        warehouse["shipboardDataWarehouseBaseDir"], args.cruise_id, ""
    )
    if not os.path.isdir(source):
        print(f"Source directory not found: {source}", file=sys.stderr)
        return 2

    try:
        destination = resolve_destination(transfer, args.cruise_id)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    output_stem = f"{safe_filename(args.cruise_id)}-{safe_filename(args.transfer)}"
    exclude_file = args.exclude_file or Path("/var/tmp") / f"{output_stem}.excludes"
    log_file = args.log_file or Path("/var/tmp") / f"{output_stem}.check.log"

    excludes = build_excludes(ovdm, args.cruise_id, transfer, warehouse, source)
    write_excludes(exclude_file, excludes)

    print(f"Cruise:      {args.cruise_id}")
    print(f"Transfer:    {args.transfer}")
    configured_mode = "sync" if int(transfer.get("syncToDest", 0)) == 1 else "copy"
    print(f"Configured:  {configured_mode}")
    print(f"Source:      {source}")
    print(f"Destination: {destination}")
    print(f"Exclude file: {exclude_file}")
    print(f"Check log:    {log_file}")
    print(f"Exclude patterns ({len(excludes)}):")
    for pattern in excludes:
        print(f"  {pattern}")

    if configured_mode != "sync":
        print(
            "WARNING: the saved Cruise Data Transfer is configured for copy, not sync",
            file=sys.stderr,
        )

    if args.excludes_only:
        return 0

    try:
        print("\nCalculating transferable sizes...")
        source_size = rclone_size(source, exclude_file)
        destination_size = rclone_size(destination, exclude_file)
    except subprocess.CalledProcessError as error:
        print(f"Unable to calculate sizes: {error}", file=sys.stderr)
        if error.stderr:
            print(error.stderr.strip(), file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"Unable to parse rclone size output: {error}", file=sys.stderr)
        return 2

    print(
        f'Source: {source_size["count"]:,} files, '
        f'{human_size(source_size["bytes"])}'
    )
    print(
        f'Bucket: {destination_size["count"]:,} objects, '
        f'{human_size(destination_size["bytes"])}'
    )

    print("\nRunning read-only verification...")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("", encoding="utf-8")
    check_status = run_check(source, destination, exclude_file, log_file)
    if check_status == 0:
        print("PASS: all included source files exist at the destination with matching sizes")
        return 0

    print(f"FAIL: rclone check exited with status {check_status}", file=sys.stderr)
    return offer_resync(
        ovdm,
        args,
        source,
        destination,
        exclude_file,
        log_file,
    )


if __name__ == "__main__":
    raise SystemExit(main())
