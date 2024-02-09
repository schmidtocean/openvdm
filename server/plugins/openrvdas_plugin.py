#!/usr/bin/env python3
"""

FILE:  openrvdas_plugin.py

USAGE:  openrvdas_plugin.py [-h] [--dataType] <dataFile>

DESCRIPTION:  This python script interprets raw files created by the OpenRVDAS
    Data Acquision System.  Depending on the command-line arguments, the script
    returns the data type of the file or a sub-sampled and json-formatted
    version of the original file to stdout.  The json-formatted file is
    used by OpenVDM as part of it's Data dashboard.

  OPTIONS:  [-h] Return the help message.
            [--dataType] Return the datatype of the file as defined in the
                fileTypeFilter array.
            <dataFile> Full or relative path of the data file to process.

REQUIREMENTS:  Python3.8
            Python Modules:

     BUGS:
    NOTES:
   AUTHOR:  Webb Pinner
  VERSION:  1.0
  CREATED:  2016-10-23
 REVISION:  2021-02-13
"""

import sys
import os
import fnmatch
import argparse
import logging

from os.path import dirname, realpath
sys.path.append(dirname(dirname(dirname(realpath(__file__)))))

from server.lib.openvdm import OpenVDM
from server.lib.openvdm_plugin import OpenVDMPlugin
from server.plugins.parsers.dbs_parser       import DBSParser
from server.plugins.parsers.dpt_parser       import DPTParser
# from server.plugins.parsers.flowrate_parser  import FlowrateParser
# from server.plugins.parsers.fluoro_parser    import FluoroParser
from server.plugins.parsers.gga_parser       import GGAParser
# from server.plugins.parsers.ggk_parser       import GGKParser
# from server.plugins.parsers.gll_parser       import GLLParser
# from server.plugins.parsers.gst_parser       import GSTParser
from server.plugins.parsers.hdt_parser       import HDTParser
from server.plugins.parsers.metpakpro_parser import MetPakProParser
from server.plugins.parsers.minisvs_parser   import MiniSVSParser
# from server.plugins.parsers.mwd_parser       import MWDParser
# from server.plugins.parsers.par2_parser      import PARParser as RADParser
# from server.plugins.parsers.par_parser       import PARParser
from server.plugins.parsers.pashr_parser     import PashrParser
# from server.plugins.parsers.prdid_parser   import PRDIDParser
# from server.plugins.parsers.rmc_parser       import RMCParser
# from server.plugins.parsers.rot_parser       import ROTParser
from server.plugins.parsers.svp_parser       import SVPParser
from server.plugins.parsers.tsg_parser     import TSGParser
from server.plugins.parsers.vtg_parser       import VTGParser

cruiseID = OpenVDM().get_cruise_id()

# -------------------------------------------------------------------------------------
# This array defines the various dataTypes collected by SCS and the cooresponding file
# regex expression.
# -------------------------------------------------------------------------------------
fileTypeFilters = [
    {"data_type":"dps122-gga",       "regex": "*/" + cruiseID + "_dps122_gga-*.txt",      "parser": "GGA",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"dps122-vtg",       "regex": "*/" + cruiseID + "_dps122_vtg-*.txt",      "parser": "VTG",       'parser_options':{'skip_header':True,'use_openvdm_api':True,'no_mag':True}},
    {"data_type":"ea440-dbs",        "regex": "*/" + cruiseID + "_ea440_dbs-*.txt",       "parser": "DBS",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"ea440-dpt",        "regex": "*/" + cruiseID + "_ea440_dpt-*.txt",       "parser": "DPT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"ea640-dbs",        "regex": "*/" + cruiseID + "_ea640_dbs-*.txt",       "parser": "DBS",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"ea640-dpt",        "regex": "*/" + cruiseID + "_ea640_dpt-*.txt",       "parser": "DPT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"em124-dpt",        "regex": "*/" + cruiseID + "_em124_dpt-*.txt",       "parser": "DPT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"em2040-dpt",       "regex": "*/" + cruiseID + "_em2040_dpt-*.txt",      "parser": "DPT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"em712-dpt",        "regex": "*/" + cruiseID + "_em712_dpt-*.txt",       "parser": "DPT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"flowrate-aft",     "regex": "*/" + cruiseID + "_flowrate_aft-*.txt",    "parser": "Flowrate",  'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"flowrate-fwd",     "regex": "*/" + cruiseID + "_flowrate_fwd-*.txt",    "parser": "Flowrate",  'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"fluorometer",      "regex": "*/" + cruiseID + "_fluorometer-*.txt",     "parser": "Fluoro",    'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"gyro1-hdt",        "regex": "*/" + cruiseID + "_gyro_1_hdt-*.txt",     "parser": "HDT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"gyro1-rot",        "regex": "*/" + cruiseID + "_gyro_1_rot-*.txt",     "parser": "ROT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"gyro2-hdt",        "regex": "*/" + cruiseID + "_gyro_2_hdt-*.txt",     "parser": "HDT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"gyro2-rot",        "regex": "*/" + cruiseID + "_gyro_2_rot-*.txt",     "parser": "ROT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"gyro3-hdt",        "regex": "*/" + cruiseID + "_gyro_3_hdt-*.txt",     "parser": "HDT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"gyro3-rot",        "regex": "*/" + cruiseID + "_gyro_3_rot-*.txt",     "parser": "ROT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"minisvs-aft",      "regex": "*/" + cruiseID + "_minisvs_aft-*.txt",     "parser": "MiniSVS",   'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"minisvs-fwd",      "regex": "*/" + cruiseID + "_minisvs_fwd-*.txt",     "parser": "MiniSVS",   'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"mpp-mm-aft",         "regex": "*/" + cruiseID + "_mpp_mm_aft-*.txt",    "parser": "MetPakPro", 'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"par",              "regex": "*/" + cruiseID + "_par-*.txt",             "parser": "PAR",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"posmv-gga",        "regex": "*/" + cruiseID + "_posmv_gga-*.txt",       "parser": "GGA",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"posmv-ggk",        "regex": "*/" + cruiseID + "_posmv_ggk-*.txt",       "parser": "GGK",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"posmv-gll",        "regex": "*/" + cruiseID + "_posmv_gll-*.txt",       "parser": "GLL",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"posmv-gst",        "regex": "*/" + cruiseID + "_posmv_gst-*.txt",       "parser": "GST",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"posmv-hdt",        "regex": "*/" + cruiseID + "_posmv_hdt-*.txt",       "parser": "HDT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"posmv-pashr",      "regex": "*/" + cruiseID + "_posmv_pashr-*.txt",     "parser": "Pashr",     'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"posmv-rmc",        "regex": "*/" + cruiseID + "_posmv_rmc-*.txt",       "parser": "RMC",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"posmv-vtg",        "regex": "*/" + cruiseID + "_posmv_vtg-*.txt",       "parser": "VTG",       'parser_options':{'skip_header':True,'use_openvdm_api':True,'no_mag':True}},
    # {"data_type":"rad",              "regex": "*/" + cruiseID + "_rad-*.txt",             "parser": "RAD",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"seapath-gga",      "regex": "*/" + cruiseID + "_seapath_gga-*.txt",     "parser": "GGA",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"seapath-hdt",      "regex": "*/" + cruiseID + "_seapath_hdt-*.txt",     "parser": "HDT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"seapath-prdid",    "regex": "*/" + cruiseID + "_seapath_prdid-*.txt",   "parser": "PRDID",     'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"seapath-rmc",      "regex": "*/" + cruiseID + "_seapath_rmc-*.txt",     "parser": "RMC",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"seapath-rot",      "regex": "*/" + cruiseID + "_seapath_rot-*.txt",     "parser": "ROT",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"seapath-vtg",      "regex": "*/" + cruiseID + "_seapath_vtg-*.txt",     "parser": "VTG",       'parser_options':{'skip_header':True,'use_openvdm_api':True,'no_mag':True}},
    {"data_type":"tsg45_1",          "regex": "*/" + cruiseID + "_tsg_sbe45_1-*.txt",     "parser": "TSG",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    {"data_type":"tsg45_2",          "regex": "*/" + cruiseID + "_tsg_sbe45_2-*.txt",     "parser": "TSG",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"truewind-port",    "regex": "*/" + cruiseID + "_truewind_port-*.txt",   "parser": "MWD",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
    # {"data_type":"truewind-stbd",    "regex": "*/" + cruiseID + "_truewind_stbd-*.txt",   "parser": "MWD",       'parser_options':{'skip_header':True,'use_openvdm_api':True}},
]

# -------------------------------------------------------------------------------------
# Function to determine the datatype of the raw datafile.  If the datatype can not be
# determined, the function returns false
# -------------------------------------------------------------------------------------


class OpeRVDASPlugin(OpenVDMPlugin):
    """
    OpenVDM plugin for the SCS Underway data acquisition system
    """

    def __init__(self):
        super().__init__(fileTypeFilters)

    def get_parser(self, filepath): # pylint: disable=too-many-return-statements
        """
        Function to determine the parser to use with the raw datafile.  If the
        datatype can not be determined, the function returns false
        """

        file_type_filter = list(filter(lambda file_type_filter: fnmatch.fnmatch(filepath, file_type_filter['regex']), self.file_type_filters))

        if len(file_type_filter) == 0:
            return None

        file_type_filter = file_type_filter[0]

        if file_type_filter['parser'] == "GGA":
            return GGAParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "TSG":
            return TSGParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "MWD":
            return MWDParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "SVP":
            return SVPParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "MetPakPro":
            return MetPakProParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "TSG":
            return TSGParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "ROT":
            return ROTParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "RMC":
            return RMCParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "GLL":
            return GLLParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "GGK":
            return GGKParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "PAR":
            return PARParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "MiniSVS":
            return MiniSVSParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "GST":
            return GSTParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "Pashr":
            return PashrParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "PRDID":
            return PRDIDParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "RAD":
            return RADParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "Fluoro":
            return FluoroParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "Flowrate":
            return FlowrateParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "HDT":
            return HDTParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "DBS":
            return DBSParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "DPT":
            return DPTParser(**file_type_filter['parser_options'])

        if file_type_filter['parser'] == "VTG":
            return VTGParser(**file_type_filter['parser_options'])

        return None


# -------------------------------------------------------------------------------------
# Required python code for running the script as a stand-alone utility
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OpenVDM plugin for OpenRVDAS')
    parser.add_argument('--dataType', action='store_true',
                        help='return the dataType of the file')
    parser.add_argument('-v', '--verbosity', dest='verbosity',
                        default=0, action='count',
                        help='Increase output verbosity')
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

    if not os.path.isfile(parsed_args.dataFile):
        logging.error("File not found")
        sys.exit(1)
    elif os.stat(parsed_args.dataFile).st_size == 0:
        logging.warning("File is empty")
        sys.exit(0)

    plugin = OpeRVDASPlugin()

    if parsed_args.dataType:
        dataType = plugin.get_data_type(parsed_args.dataFile)
        if dataType is None:
            logging.warning("File is of unknown type")
            sys.exit(1)
        print(dataType)
    else:
        jsonSTR = plugin.get_json_str(parsed_args.dataFile)
        if jsonSTR is None:
            logging.warning("Nothing returned from parser")
            sys.exit(1)
        print(jsonSTR)
