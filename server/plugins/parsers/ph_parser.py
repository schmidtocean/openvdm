#!/usr/bin/env python3
"""
FILE:  ph_parser.py

USAGE:  ph_parser.py [-h] [-v+] [--timeFormat] [--startDT] [--stopDT] <dataFile>

DESCRIPTION:  Parse the supplied pH sensor data and return the json-formatted string
    used by OpenVDM as part of it's Data dashboard.

  OPTIONS:  [-h] Return the help message.
            [-v+] Increase verbosity (default: warning)
            [--timeFormat] date/time format to use when parsing datafile, default
                           yyyy-mm-ddTHH:MM:SS.sssZ
            [--startTS] optional start crop time (strptime format)
            [--stopTS] optional stop crop time (strptime format)
            <dataFile> Full or relative path of the data file to process.

REQUIREMENTS:  Python3.8
            Python Modules:
                numpy==1.19.5
                pandas==1.2.0
                PyYAML==5.3.1
                requests==2.25.1

     BUGS:
    NOTES:
   AUTHOR:  Webb Pinner
  VERSION:  2.6
  CREATED:  2016-08-29
 REVISION:  2021-02-13
"""

import sys
import csv
import json
import logging
from copy import deepcopy
from datetime import datetime
from os.path import dirname, realpath
import pandas as pd

sys.path.append(dirname(dirname(dirname(dirname(realpath(__file__))))))

from server.lib.openvdm_plugin import OpenVDMCSVParser
from server.lib.condense_to_ranges import condense_to_ranges

RAW_COLS = ['date','time','jday','temp','salinity','ph','voltage'] # OpenRVDAS style
# RAW_COLS = ['date','time','jday','temp','salinity','ph','voltage'] # SCS style
PROC_COLS = ['date_time','temp','ph']

ROUNDING = {
    'temp': 2,
    'ph': 2
}

MAX_DELTA_T = pd.Timedelta('10 seconds')

DEFAULT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" # ISO8601 Format, OpenRVDAS style
# DEFAULT_TIME_FORMAT = "%m/%d/%Y %H:%M:%S.%f" # SCS style


class PHParser(OpenVDMCSVParser):
    """
    Custom OpenVDM CSV file parser
    """

    def __init__(self, start_dt=None, stop_dt=None, time_format=None, skip_header=False, use_openvdm_api=False):
        super().__init__(RAW_COLS, PROC_COLS, start_dt=start_dt, stop_dt=stop_dt, time_format=time_format, skip_header=skip_header, use_openvdm_api=use_openvdm_api)


    def process_file(self, filepath): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the provided file
        """

        raw_into_df = { value: [] for key, value in enumerate(self.proc_cols) }

        logging.debug("Parsing data file...")
        errors = []
        try:
            with open(filepath, mode='r', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, self.raw_cols)

                if self.skip_header:
                    next(reader)

                for lineno, line in enumerate(reader):

                    try:
                        date_time = line['date_time'] # OpenRVDAS style
                        # date_time = ' '.join([line['date'], line['time']]) # SCS style

                        ph_data = float(line['ph'])

                    except Exception as err:
                        errors.append(lineno)
                        logging.warning("Parsing error encountered on line %s", lineno)
                        logging.debug(line)
                        logging.debug(str(err))

                    else:
                        raw_into_df['date_time'].append(date_time)
                        raw_into_df['ph'].append(ph_data)

        except Exception as err:
            logging.error("Problem accessing input file: %s", filepath)
            logging.error(str(err))
            return

        logging.debug("Finished parsing data file")

        # If no data ingested from file, quit
        if len(raw_into_df['date_time']) == 0:
            logging.warning("Dataframe is empty... quitting")
            return

        # Build DataFrame
        logging.debug("Building dataframe from parsed data...")
        df_proc = pd.DataFrame(raw_into_df)

        # Convert Date/time column to datetime objects
        logging.debug("Converting data_time to datetime datatype...")

        df_proc['date_time'] = pd.to_datetime(df_proc['date_time'], format=self.time_format)

        # Optionally crop data by start/stop times
        if self.start_dt or self.stop_dt:
            logging.debug("Cropping data...")

            df_proc = self.crop_data(df_proc)

        # If the crop operation emptied the dataframe, quit
        if df_proc.shape[0] == 0:
            logging.warning("Cropped dataframe is empty... quitting")
            return

        # Calculate deltaT column
        logging.debug('Building deltaT column...')
        df_proc = df_proc.join(df_proc['date_time'].diff().to_frame(name='deltaT'))

        logging.debug("Tabulating statistics...")
        self.add_row_validity_stat([len(df_proc), len(errors)])
        self.add_time_bounds_stat([df_proc['date_time'].min(), df_proc['date_time'].max()])
        self.add_bounds_stat([round(df_proc['deltaT'].min().total_seconds(),3), round(df_proc['deltaT'].max().total_seconds(),3)], 'DeltaT Bounds', 'seconds')
        self.add_value_validity_stat([len(df_proc[(df_proc['deltaT'] <= MAX_DELTA_T)]),len(df_proc[(df_proc['deltaT'] > MAX_DELTA_T)])], 'DeltaT Validity')
        self.add_bounds_stat([round(df_proc['temp'].min(),2), round(df_proc['temp'].max(),2)], 'Temperature Bounds', 'C')
        self.add_bounds_stat([round(df_proc['ph'].min(),1), round(df_proc['ph'].max(),1)], 'pH Bounds')

        logging.debug("Running quality tests...")
        # % of bad rows in datafile
        error_rate = len(errors) / (len(df_proc) + len(errors))
        if error_rate > .25:
            self.add_quality_test_failed("Rows")
        elif error_rate > .10:
            self.add_quality_test_warning("Rows")
        else:
            self.add_quality_test_passed("Rows")

        # % of time gaps in data
        error_rate = len(df_proc[(df_proc['deltaT'] > MAX_DELTA_T)]) / len(df_proc)
        if error_rate > .25:
            self.add_quality_test_failed("DeltaT")
        elif error_rate > .10:
            self.add_quality_test_warning("DeltaT")
        else:
            self.add_quality_test_passed("DeltaT")

        # set index
        logging.debug('Setting index...')
        df_proc = df_proc.set_index('date_time')

        # resample data
        logging.debug("Resampling data...")
        df_proc = self.resample_data(df_proc)

        # round data
        logging.debug("Rounding data: %s", ROUNDING)
        df_proc = self.round_data(df_proc, ROUNDING)

        # split data where there are gaps
        logging.debug("Building visualization data...")

        visualizer_data_obj = {'data':[], 'unit':'', 'label':''}
        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','temp']].to_json(orient='values'))
        visualizer_data_obj['unit'] = 'C'
        visualizer_data_obj['label'] = 'Temperature'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        visualizer_data_obj = {'data':[], 'unit':'', 'label':''}
        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','ph']].to_json(orient='values'))
        visualizer_data_obj['unit'] = ''
        visualizer_data_obj['label'] = 'pH'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        # send message about errors encountered to OpenVDM
        if self.openvdm is not None and len(errors) > 0:
            self.openvdm.send_msg('Parsing Error', f'Error(s) parsing datafile {filepath} on row(s): {", ".join(condense_to_ranges(errors))}')


# -------------------------------------------------------------------------------------
# Required python code for running the script as a stand-alone utility
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse pH sensor data')
    parser.add_argument('-v', '--verbosity', dest='verbosity',
                        default=0, action='count',
                        help='Increase output verbosity')
    parser.add_argument('--timeFormat', default=DEFAULT_TIME_FORMAT,
                        help='timestamp format, default: %(default)')
    parser.add_argument('--startDT', default=None,
                        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ'),
                        help=' crop start timestamp (iso8601)')
    parser.add_argument('--stopDT', default=None,
                        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ'),
                        help=' crop stop timestamp (iso8601)')
    parser.add_argument('dataFile', metavar='dataFile',
                        help='the raw data file to process')

    parsed_args = parser.parse_args()

    ############################
    # Set up logging before we do any other argument parsing (so that we
    # can log problems with argument parsing).

    LOGGING_FORMAT = '%(asctime)-15s %(levelname)s - %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)

    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    parsed_args.verbosity = min(parsed_args.verbosity, max(LOG_LEVELS))
    logging.getLogger().setLevel(LOG_LEVELS[parsed_args.verbosity])

    ovdm_parser = PHParser(start_dt=parsed_args.startDT, stop_dt=parsed_args.stopDT, time_format=parsed_args.timeFormat, use_openvdm_api=False)

    try:
        logging.info("Processing file: %s", parsed_args.dataFile)
        ovdm_parser.process_file(parsed_args.dataFile)
        print(ovdm_parser.to_json())
        logging.info("Done!")
    except Exception as err:
        logging.error(str(err))
        raise err
