#!/bin/bash

# Get the current directory
current_dir=$(pwd)

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

cd $install_dir

# Directory containing SQL files
sql_directory="$install_dir/database/backups"

# MySQL connection parameters
mysql_database=$1
mysql_user=$2
mysql_password=$3

# Function to display menu and prompt user for selection
select_sql_file() {
    local files=("$sql_directory"/*.sql)
    local selected_file

    echo "Select SQL file to restore:"
    select filename in "${files[@]}"; do
        selected_file="$filename"
        break
    done

    echo "You selected: $selected_file"
    restore_database "$selected_file"
}

# Function to restore MySQL database from selected SQL file
restore_database() {
    local sql_file="$1"
    read -p "Enter MySQL root password: " -s root_password
    echo # For newline after password input

    # Check if the file exists
    if [ ! -f "$sql_file" ]; then
        echo "File not found: $sql_file"
        exit 1
    fi

    # Restore the database
    mysql -u"$mysql_user" -p"$mysql_password" "$mysql_database" < "$sql_file"

    if [ $? -eq 0 ]; then
        echo "Database restored successfully."
    else
        echo "Database restore failed."
    fi
}

# Main function
main() {
    select_sql_file
}

# Entry point
main
