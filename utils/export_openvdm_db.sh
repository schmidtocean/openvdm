#!/usr/bin/bash

# This script exports the openvdm database to stdout. Use redirect to save the
# output to file.
#
# This script does not export the contents of the messages
# table.    
#
# This script assumes the name of the OpenVDM database is "openvdm"
#

DATABASE=openvdm

mysqldump $DATABASE -p --ignore-table=openvdm.OVDM_Messages --ignore-table=openvdm.OVDM_Gearman
mysqldump $DATABASE -p --no-data OVDM_Messages --no-data OVDM_Gearman