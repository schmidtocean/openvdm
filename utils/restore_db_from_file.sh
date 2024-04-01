#!/bin/bash

# Get the current directory
current_dir=$(pwd)

DATABASE='openvdm'
USER='openvdmDBUser'
BACKUP_DIR='/opt/openvdm/database/backups'
UPDATE_CORE_VARS=0

# Function to display usage information
usage() {
    echo "Usage: $0 [-d database] [-u user] [-b backup_dir] password"
    echo "Options:"
    echo "  -d, --database    Specify OpenVDM database (default: $DATABASE)"
    echo "  -u, --user        Specify the database user (default: $USER)"
    echo "  -b, --backup_dir  Specify the database backup directory (default: ${BACKUP_DIR})"
    echo "  -c, --core_vars   Update the CoreVars table (Potentially dangerous)"
    echo "  password          Specify the password for the db user"
    exit 1
}

# Parse command line options
parse_cmd_args() {
    while [[ $# -gt 1 ]]; do
        key="$1"
        case $key in
            -d|--database)
                DATABASE="$2"
                shift 2
                ;;
            -u|--user)
                USER="$2"
                shift 2
                ;;
            -b|--backup_dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            -c|--core_vars)
                UPDATE_CORE_VARS=1
                shift 1
                ;;
            *)
                # Unknown option
                usage
                ;;
        esac
    done

    if [[ $# -eq 0 ]]; then
        usage
    fi
    PASSWD=$1

    # Verify backup directory exists
    if [[ ! -d $BACKUP_DIR ]]; then
        echo "ERROR: Backup directory: $BACKUP_DIR does not exist"
        echo
        usage
    fi
}

# Function to handle errors
handle_error() {
    echo "Error occurred in script at line $1."
    # You can add additional error handling logic here
    cd $current_dir
    exit 1
}

# Set up error handling
trap 'handle_error $LINENO' ERR

# Get the directory of the script
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Script directory is: $script_dir"

# Get the parent directory
install_dir="$(dirname "$script_dir")"
echo "Install directory is: $install_dir"

# Function to display menu and prompt user for selection
select_sql_file() {
    cd $BACKUP_DIR
    local files=(*.sql)
    cd $current_dir

    local selected_file

    echo "Select SQL file to restore:"
    select opt in ${files} "Cancel"; do
        if [ $opt == "Cancel" ]; then
            exit 0
        fi

        selected_file="$opt"
        break
    done

    echo "You selected: $selected_file"
    restore_database "$selected_file"
}

# Function to restore MySQL database from selected SQL file
restore_database() {
    local sql_file="$1"
    local ignore_core_vars="$2"

    temp_file=$(mktemp)
    cat $BACKUP_DIR/$sql_file > $temp_file

    if [[ $UPDATE_CORE_VARS -eq 1 ]]; then

        echo "ignore CoreVars table"
        # Tables to exclude from restoration
        excluded_tables=("OVDM_CoreVars")

        # Exclude the specific table from the SQL file
        temp2_file=$(mktemp)

        for table in "${excluded_tables[@]}"; do
            sed -e "/DROP TABLE IF EXISTS \`${table}\`;/d" \
                -e "/CREATE TABLE \`${table}\`/,/;/d" \
                -e "/INSERT INTO \`${table}\`/d" \
                -e "/LOCK TABLES \`${table}\` WRITE;/d" \
                $temp_file > $temp2_file && mv $temp2_file $temp_file
        done
    fi


    # Restore the database
    echo "mysql -u $USER -p $PASSWD $DATABASE < $temp_file"
    # mysql -u"$USER" -p"$PASSWD" "$DATABASE" < $temp_file

    if [ $? -eq 0 ]; then
        echo "Database restored successfully."
    else
        echo "ERROR: Database restore failed."
    fi

    rm $temp_file
}

# Main function
main() {
    parse_cmd_args "$@"
    select_sql_file
}

# Entry point
main "$@"
