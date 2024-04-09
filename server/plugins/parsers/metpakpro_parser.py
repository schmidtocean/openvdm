#!/usr/bin/env python3
"""
FILE:  metpakpro_parser.py

USAGE:  metpakpro_parser.py [-h] [-v+] [--timeFormat] [--startDT] [--stopDT] <dataFile>

DESCRIPTION:  Parse the supplied MetPakPro sensor data file and return the json-
    formatted string used by OpenVDM as part of it's Data dashboard.

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
  VERSION:  2.9
  CREATED:  2016-08-29
 REVISION:  2022-07-24
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

RAW_COLS = ['date_time','node_letter','wind_dir','wind_spd','air_pres','humidity','air_temp','dew_point','prt','humidity','analog_1','analog_2','digital_1','digital_2','supply_voltage','supply_code','checksum'] # OpenRVDAS style
# RAW_COLS = ['date','time','node_letter','wind_dir','wind_spd','air_pres','humidity','air_temp','dew_point','prt','humidity','analog_1','analog_2','digital_1','digital_2','supply_voltage','supply_code','checksum'] # SCS style
PROC_COLS = ['date_time','air_pres','air_temp','humidity','wind_spd','wind_dir']

ROUNDING = {
    'air_pres': 1,
    'air_temp': 2,
    'humidity': 1,
    'wind_spd': 1,
    'wind_dir': 1
}

MAX_DELTA_T = pd.Timedelta('10 seconds')


class MetPakProParser(OpenVDMCSVParser):
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

                        air_pres = float(line['air_pres'])
                        air_temp = float(line['air_temp'])
                        humidity = float(line['humidity'])
                        wind_spd = float(line['wind_spd'])
                        wind_dir = float(line['wind_dir'])

                    except Exception as err:
                        errors.append(lineno)
                        logging.warning("Parsing error encountered on line %s", lineno)
                        logging.debug(line)
                        logging.debug(str(err))

                    else:
                        raw_into_df['date_time'].append(date_time)
                        raw_into_df['air_pres'].append(air_pres)
                        raw_into_df['air_temp'].append(air_temp)
                        raw_into_df['humidity'].append(humidity)
                        raw_into_df['wind_spd'].append(wind_spd)
                        raw_into_df['wind_dir'].append(wind_dir)

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
        self.add_bounds_stat([round(df_proc['wind_spd'].min(),1), round(df_proc['wind_spd'].max(),1)], 'Wind Speed Bounds', 'm/s')
        self.add_bounds_stat([round(df_proc['air_temp'].min(),2), round(df_proc['air_temp'].max(),2)], 'Air Temperature Bounds', 'C')
        self.add_bounds_stat([round(df_proc['air_pres'].min(),1), round(df_proc['air_pres'].max(),1)], 'Air Pressure Bounds', 'hPa')

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
        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','air_pres']].to_json(orient='values'))
        visualizer_data_obj['unit'] = 'hPa'
        visualizer_data_obj['label'] = 'Air Pressure'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','air_temp']].to_json(orient='values'))
        visualizer_data_obj['unit'] = 'C'
        visualizer_data_obj['label'] = 'Air Temperature'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','humidity']].to_json(orient='values'))
        visualizer_data_obj['unit'] = '%'
        visualizer_data_obj['label'] = 'Relative Humidity'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','wind_spd']].to_json(orient='values'))
        visualizer_data_obj['unit'] = 'm/s'
        visualizer_data_obj['label'] = 'Relative Wind Spd'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        visualizer_data_obj['data'] = json.loads(df_proc[['date_time','wind_dir']].to_json(orient='values'))
        visualizer_data_obj['unit'] = 'deg'
        visualizer_data_obj['label'] = 'Relative Wind Dir'
        self.add_visualization_data(deepcopy(visualizer_data_obj))

        # send message about errors encountered to OpenVDM
        if self.openvdm is not None and len(errors) > 0:
            self.openvdm.send_msg('Parsing Error', f'Error(s) parsing datafile {filepath} on row(s): {", ".join(condense_to_ranges(errors))}')


# -------------------------------------------------------------------------------------
# Required python code for running the script as a stand-alone utility
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parse MetPakPro Sensor data')
    parser.add_argument('-v', '--verbosity', dest='verbosity',
                        default=0, action='count',
                        help='Increase output verbosity')
    parser.add_argument('--timeFormat', help='timestamp format', default=None)
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

    ovdm_parser = MetPakProParser(start_dt=parsed_args.startDT, stop_dt=parsed_args.stopDT, time_format=parsed_args.timeFormat)

    try:
        logging.info("Processing file: %s", parsed_args.dataFile)
        ovdm_parser.process_file(parsed_args.dataFile)
        print(ovdm_parser.to_json())
        logging.info("Done!")
    except Exception as err:
        logging.error(str(err))
        raise err
