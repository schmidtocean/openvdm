#!/usr/bin/env python3
"""
Standalone OpenVDM -> Metadata Manager calibration report hook.

   python /opt/openvdm/bin/metadataman_pull_calibration_report.py \
     --cruise-id FKt260501 \
     --cruise-start-date "2026/05/01 00:00" \
     --cruise-end-date "2026/05/10 23:59" \
     --verbose

OpenVDM post-hook config invokes this from:
   /opt/openvdm/bin/metadataman_pull_calibration_report.py

Auth: set METADATA_MANAGER_REFRESH_TOKEN or METADATA_MANAGER_ACCESS_TOKEN.
To copy a readonly user's refresh token from the web app console:
copy(JSON.parse(localStorage.getItem("soiMetadataManagerAuthCredentials")).refresh_token)

Defaults:
- OpenVDM dates are read from getCruiseStartDate/getCruiseEndDate when omitted.
- ZIP download: system temp dir / $cruiseID / <report>.zip
- Unpack destination: /mnt/CruiseData/$cruiseID/Docs/
- Use -vv for HTTP details.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


REPORT_TYPE = "installation_timeline_with_calibration_status"
DEFAULT_OPENVDM_CRUISE_ID = os.environ.get("OPENVDM_CRUISE_ID")
DEFAULT_CRUISE_START_DATE = None
DEFAULT_CRUISE_END_DATE = None
DEFAULT_OPENVDM_SITE_ROOT = os.environ.get(
    "OPENVDM_SITE_ROOT",
    "http://10.23.9.20/",
)
DEFAULT_METADATA_BASE_URL = os.environ.get(
    "METADATA_MANAGER_BASE_URL",
    "https://metadata-manager-back-end-380627628202.us-west1.run.app",
)
DEFAULT_METADATA_ACCESS_TOKEN = os.environ.get("METADATA_MANAGER_ACCESS_TOKEN")
DEFAULT_METADATA_REFRESH_TOKEN = os.environ.get("METADATA_MANAGER_REFRESH_TOKEN")
DEFAULT_OUTPUT_DIR = os.environ.get(
    "METADATA_MANAGER_HOOK_OUTPUT_DIR",
    tempfile.gettempdir(),
)
DEFAULT_UNPACK_ROOT = os.environ.get("METADATA_MANAGER_UNPACK_ROOT", "/mnt/CruiseData")
DEFAULT_UNPACK_DIR = os.environ.get("METADATA_MANAGER_UNPACK_DIR")
DEFAULT_TIMEOUT = 300
DEFAULT_DOWNLOAD_TIMEOUT = int(
    os.environ.get("METADATA_MANAGER_DOWNLOAD_TIMEOUT_SECONDS", "1800")
)
DEFAULT_VERBOSITY = 0


class HookError(RuntimeError):
    pass


logger = logging.getLogger("openvdm_metadata_calibration_report")


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_headers = {"Accept": "application/json"}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)

    request = Request(url, data=body, headers=request_headers, method=method)
    logger.debug("HTTP %s %s", method, url)
    try:
        with urlopen(request, timeout=timeout) as response:
            logger.debug("HTTP %s %s -> %s", method, url, response.status)
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        raise HookError(f"Request failed: {method} {url}: {exc}") from exc


def download(url: str, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    logger.debug("Downloading %s", url)
    try:
        with urlopen(Request(url, method="GET"), timeout=timeout) as response:
            content = response.read()
            logger.debug("Downloaded %s bytes from %s", len(content), url)
            return content
    except (HTTPError, URLError) as exc:
        raise HookError(f"Download failed: {url}: {exc}") from exc


def get_access_token(
    base_url: str, access_token: str | None, refresh_token: str | None
) -> str:
    if access_token:
        logger.debug("Using access token from CLI/environment")
        return access_token
    if not refresh_token:
        raise HookError(
            "Set METADATA_MANAGER_ACCESS_TOKEN or METADATA_MANAGER_REFRESH_TOKEN."
        )

    logger.info("Refreshing Metadata Manager access token")
    token_response = request_json(
        "POST",
        urljoin(ensure_slash(base_url), "refresh"),
        payload={"refresh_token": refresh_token},
    )
    token = token_response.get("access_token")
    if not token:
        raise HookError("Refresh did not return access_token.")
    return token


def get_openvdm_value(site_root: str, endpoint: str, key: str, timeout: int) -> str:
    logger.info("Reading %s from OpenVDM endpoint %s", key, endpoint)
    response = request_json(
        "GET",
        urljoin(ensure_slash(site_root), endpoint),
        timeout=timeout,
    )
    value = response.get(key)
    if not value:
        raise HookError(f"OpenVDM did not return {key}.")
    return value


def to_metadata_datetime(value: str) -> str:
    parsed = parse_datetime(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def parse_datetime(value: str) -> datetime:
    normalized = value.strip()
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        pass

    for fmt in (
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    raise HookError(f"Unsupported datetime format: {value}")


def ensure_slash(url: str) -> str:
    return url if url.endswith("/") else f"{url}/"


def safe_path_segment(value: str) -> str:
    safe = value.strip().replace("/", "_").replace("\\", "_")
    if not safe or safe in {".", ".."}:
        raise HookError(f"Invalid cruise ID: {value}")
    return safe


def unpack_zip(zip_path: Path, destination: Path) -> None:
    owner = None
    if os.geteuid() == 0:
        owner_reference = destination.parent
        while not owner_reference.exists() and owner_reference != owner_reference.parent:
            owner_reference = owner_reference.parent
        if owner_reference.exists():
            owner_stat = owner_reference.stat()
            owner = (owner_stat.st_uid, owner_stat.st_gid)

    destination.mkdir(parents=True, exist_ok=True)
    destination_resolved = destination.resolve()

    with zipfile.ZipFile(zip_path) as archive:
        members = archive.infolist()
        for member in members:
            target = (destination / member.filename).resolve()
            if (
                target != destination_resolved
                and destination_resolved not in target.parents
            ):
                raise HookError(
                    f"Refusing to unpack unsafe ZIP path: {member.filename}"
                )

        archive.extractall(destination)

    if owner:
        extracted_paths = {destination}
        for member in members:
            target = destination / member.filename
            while target != destination.parent:
                extracted_paths.add(target)
                if target == destination:
                    break
                target = target.parent

        for target in extracted_paths:
            if target.exists() and not target.is_symlink():
                os.chown(target, *owner)
        logger.info(
            "Set report ownership to uid=%s gid=%s from %s",
            owner[0],
            owner[1],
            destination.parent,
        )


def run(args: argparse.Namespace) -> dict[str, str | None]:
    metadata_base_url = ensure_slash(args.metadata_base_url)
    openvdm_site_root = ensure_slash(args.openvdm_site_root)
    logger.info("Metadata Manager API: %s", metadata_base_url)
    logger.info("OpenVDM API root: %s", openvdm_site_root)

    cruise_id = args.cruise_id or get_openvdm_value(
        openvdm_site_root, "api/warehouse/getCruiseID", "cruiseID", args.timeout
    )
    logger.info("Cruise ID: %s", cruise_id)
    start = args.cruise_start_date
    end = args.cruise_end_date
    if not start:
        start = get_openvdm_value(
            openvdm_site_root,
            "api/warehouse/getCruiseStartDate",
            "cruiseStartDate",
            args.timeout,
        )
    if not end:
        end = get_openvdm_value(
            openvdm_site_root,
            "api/warehouse/getCruiseEndDate",
            "cruiseEndDate",
            args.timeout,
        )
    if not start or not end:
        raise HookError("Cruise start and end dates are required.")
    logger.info("Cruise start: %s", start)
    logger.info("Cruise end: %s", end)

    access_token = get_access_token(
        metadata_base_url,
        args.access_token,
        args.refresh_token,
    )
    payload = {
        "generate_report_params": {
            "report_type": REPORT_TYPE,
            "report_params": {
                "effective_date": to_metadata_datetime(start),
                "expiration_date": to_metadata_datetime(end),
            },
        }
    }
    logger.info(
        "Requesting report %s for %s through %s",
        REPORT_TYPE,
        payload["generate_report_params"]["report_params"]["effective_date"],
        payload["generate_report_params"]["report_params"]["expiration_date"],
    )
    report = request_json(
        "POST",
        urljoin(metadata_base_url, "reports"),
        payload=payload,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=args.timeout,
    )

    filename = report.get("filename")
    download_url = report.get("download_url")
    if not filename or not download_url:
        raise HookError("Report response did not include filename and download_url.")
    logger.info("Report ready: %s", filename)
    logger.info("Download timeout: %s seconds", args.download_timeout)

    safe_cruise_id = safe_path_segment(cruise_id)
    output_dir = Path(args.output_dir) / safe_cruise_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / Path(filename).name
    logger.info("Writing report to %s", output_path)
    output_path.write_bytes(download(download_url, args.download_timeout))

    unpack_path = (
        Path(args.unpack_dir)
        if args.unpack_dir
        else Path(args.unpack_root) / safe_cruise_id / "Docs"
    )
    logger.info("Unpacking report to %s", unpack_path)
    unpack_zip(output_path, unpack_path)

    return {
        "output_path": str(output_path),
        "unpack_path": str(unpack_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cruise-id", default=DEFAULT_OPENVDM_CRUISE_ID)
    parser.add_argument("--cruise-start-date", default=DEFAULT_CRUISE_START_DATE)
    parser.add_argument("--cruise-end-date", default=DEFAULT_CRUISE_END_DATE)
    parser.add_argument(
        "--openvdm-site-root",
        default=DEFAULT_OPENVDM_SITE_ROOT,
    )
    parser.add_argument(
        "--metadata-base-url",
        default=DEFAULT_METADATA_BASE_URL,
    )
    parser.add_argument(
        "--access-token",
        default=DEFAULT_METADATA_ACCESS_TOKEN,
    )
    parser.add_argument(
        "--refresh-token",
        default=DEFAULT_METADATA_REFRESH_TOKEN,
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--unpack-root",
        default=DEFAULT_UNPACK_ROOT,
        help="Root directory used for unpacking: $root/$cruiseID/Docs.",
    )
    parser.add_argument(
        "--unpack-dir",
        default=DEFAULT_UNPACK_DIR,
        help="Exact unpack destination. Overrides --unpack-root.",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=DEFAULT_DOWNLOAD_TIMEOUT,
        help="Timeout in seconds for downloading the generated ZIP.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=DEFAULT_VERBOSITY,
        help="Print progress details. Use -vv for HTTP request details.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 1 else logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    try:
        result = run(args)
    except Exception as exc:
        print(json.dumps({"result": "Fail", "reason": str(exc)}), file=sys.stderr)
        return 1

    print(json.dumps({"result": "Pass", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
