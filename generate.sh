#!/bin/bash
#
# Author: Lixipeng <lixipeng@hihuron.com>
#
# Description: Shell command used to generate sample openstack
#              project which base on stable/liberty version.
#
# Usage: ./generate -m <manager_name> <project_name> <project_path>
#

# Global variable defination
MANAGER_NAME=${MANAGER_NAME:-}
PROJECT_NAME=${PROJECT_NAME:-}
PROJECT_PATH=${PROJECT_PATH:-}
GENERATOR_PATH=${GENERATOR_PATH:-`pwd`}

# Generator help usage
function generator_help() {
    echo -e "\033[32m"
    echo -e "Usage:\n
        generator [-m|--manager-name=MANAGER_NAME] \
PROJECT_NAME PROJET_PATH"
    echo -e "Options:\n
        -h|--help:         Show usage\n
        -m|--manager-name: Add manager for this project\n
                           and set name as manager-name"
    echo -e "\033[0m"
}

# Check whether param value is empty,
# If empty, exit with code 0
function check_empty() {
    check_param=$1
    check_val=$2
    if [ "$check_val" = "" ]; then
        echo "Param $check_param is empty."
        exit 0
    fi
}

# Check whether param value is a folder,
# If it is folder, exit with code 0
function check_exist() {
    check_param=$1
    check_val=$2
    if [ ! -d "$check_val" ]; then
        echo "Path $check_param is exist."
        exit 0
    fi
}

# Replace key value from file lists
function replace_file() {
    files=$1
    replace_old=$2
    replace_new=$3
    for item in $files;
    do
        sed -i "s/$replace_old/$replace_new/g" $PROJECT_PATH/$item
    done
}

# Fetch arguments
if [[ "$1" = "-h" || "$1" = "--help" ]]; then
    generator_help
    exit 0
elif [[ "$1" = "-m" || "$1" = "--manager-name" ]]; then
    MANAGER_NAME=$2
    check_empty "Manager name" $MANAGER_NAME
    PROJECT_NAME=$3
    check_empty "Project name" $PROJECT_NAME
    PROJECT_PATH=$4
    check_empty "Project path" $PROJECT_PATH
    check_exist "Project path" $PROJECT_PATH
elif [ "$1" = "" ]; then
    generator_help
    exit 0
else
    PROJECT_NAME=$1
    check_empty "Project name" $PROJECT_NAME
    PROJECT_PATH=$2
    check_empty "Project path" $PROJECT_PATH
    check_exist "Project path" $PROJECT_PATH
fi
PROJECT_PATH="$PROJECT_PATH/$PROJECT_NAME"

# Make project dir
if [ -d $PROJECT_PATH ]; then
    echo "$PROJECT_PATH is exist now!!!"
    exit 0
fi
mkdir $PROJECT_PATH

# Copy template files to project dir
cp -r $GENERATOR_PATH/template/* $PROJECT_PATH
cp $GENERATOR_PATH/template/.gitignore $PROJECT_PATH
cp $GENERATOR_PATH/template/.testr.conf $PROJECT_PATH

# Set first char of PROJECT_NAME upper
PROJECT_NAME_C=`echo $PROJECT_NAME|sed 's/^\(.\)/\U\1/g'`
# Set all chars of PROJECT_NAME upper
PROJECT_NAME_A=`echo $PROJECT_NAME|tr '[:lower:]' '[:upper:]'`

# Replace <project_name> with PROJECT_NAME
project_files="*.py
tox.ini
setup.cfg
run_tests.sh
*.conf
etc/*/*.conf
etc/*/*.ini
etc/*/*.conf.sample
etc/*/*/*.filters
.testr.conf
pylintrc
tools/*.py
tools/*.sh
tools/bandit.yaml
tools/config/*.sh
releasenotes/source/conf.py
.gitignore
\<project_name\>/*.py
\<project_name\>/*/*.py
\<project_name\>/*/*/*.py
\<project_name\>/*/*/*/*.py
\<project_name\>/*/*/*/*/*.py
\<project_name\>/api/schemas/v1.1/*.rng
\<project_name\>/testing/*.rst
\<project_name\>/db/sqlalchemy/migrate_repo/*.cfg
\<project_name\>/config/*.conf
\<project_name\>/locale/*.pot"
replace_file "$project_files" "<project_name>" "$PROJECT_NAME"

# Replace <Project_name> with PROJECT_NAME_C
Project_files="tools/*.py
releasenotes/source/conf.py
releasenotes/source/index.rst
*.rst
run_tests.sh
etc/*/api-paste.ini
\<project_name\>/testing/*.rst
\<project_name\>/*.py
\<project_name\>/*/*.py
\<project_name\>/*/*/*.py
\<project_name\>/*/*/*/*.py
\<project_name\>/*/*/*/*/*.py"
replace_file "$Project_files" "<Project_name>" "$PROJECT_NAME_C"

# Replace <PROJECT_NAME> with $PROJECT_NAME_A
PROJECT_files="tools/config/generate_sample.sh
*.rst
\<project_name\>/*.py
\<project_name\>/api/*.py"
replace_file "$PROJECT_files" "<PROJECT_NAME>" "$PROJECT_NAME_A"

# Rename files with <project_name>, and use PROJECT_NAME instead
# For etc/<project_name>
cp -r $PROJECT_PATH/etc/\<project_name\> $PROJECT_PATH/etc/$PROJECT_NAME
rm -r $PROJECT_PATH/etc/\<project_name\>
# For /etc/<project_name>/README-<project_name>.conf.sample
cp $PROJECT_PATH/etc/$PROJECT_NAME/README-\<project_name\>.conf.sample \
    $PROJECT_PATH/etc/$PROJECT_NAME/README-${PROJECT_NAME}.conf.sample
rm $PROJECT_PATH/etc/$PROJECT_NAME/README-\<project_name\>.conf.sample
# For etc/<project_name>/rootwrap.d/<project_name>.filters
cp $PROJECT_PATH/etc/$PROJECT_NAME/rootwrap.d/\<project_name\>.filters \
    $PROJECT_PATH/etc/$PROJECT_NAME/rootwrap.d/${PROJECT_NAME}.filters
rm $PROJECT_PATH/etc/$PROJECT_NAME/rootwrap.d/\<project_name\>.filters
# For ./<project_name>
cp -r $PROJECT_PATH/\<project_name\> $PROJECT_PATH/$PROJECT_NAME
rm -r $PROJECT_PATH/\<project_name\>
# For ./<project_name>/config/generate_<project_name>_opts.py
cp -r $PROJECT_PATH/$PROJECT_NAME/config/generate_\<project_name\>_opts.py \
    $PROJECT_PATH/$PROJECT_NAME/config/generate_${PROJECT_NAME}_opts.py
rm -r $PROJECT_PATH/$PROJECT_NAME/config/generate_\<project_name\>_opts.py
# For ./<project_name>/config/<project_name>-config-generator.conf
cp -r $PROJECT_PATH/$PROJECT_NAME/config/\<project_name\>-config-generator.conf \
    $PROJECT_PATH/$PROJECT_NAME/config/${PROJECT_NAME}-config-generator.conf
rm -r $PROJECT_PATH/$PROJECT_NAME/config/\<project_name\>-config-generator.conf
# For ./<project_name>/locale/<project_name>-log-info.pot
cp -r $PROJECT_PATH/$PROJECT_NAME/locale/\<project_name\>-log-info.pot \
    $PROJECT_PATH/$PROJECT_NAME/locale/${PROJECT_NAME}-log-info.pot
rm -r $PROJECT_PATH/$PROJECT_NAME/locale/\<project_name\>-log-info.pot
# For ./<project_name>/locale/<project_name>-log-warning.pot
cp -r $PROJECT_PATH/$PROJECT_NAME/locale/\<project_name\>-log-warning.pot \
    $PROJECT_PATH/$PROJECT_NAME/locale/${PROJECT_NAME}-log-warning.pot
rm -r $PROJECT_PATH/$PROJECT_NAME/locale/\<project_name\>-log-warning.pot
# For ./<project_name>/locale/<project_name>.pot
cp -r $PROJECT_PATH/$PROJECT_NAME/locale/\<project_name\>.pot \
    $PROJECT_PATH/$PROJECT_NAME/locale/${PROJECT_NAME}.pot
rm -r $PROJECT_PATH/$PROJECT_NAME/locale/\<project_name\>.pot
# For ./<project_name>/db/sqlalchemy/migrate_repo/versions/001_<project_name>_init.py
cp -r $PROJECT_PATH/$PROJECT_NAME/db/sqlalchemy/migrate_repo/versions/001_\<project_name\>_init.py \
    $PROJECT_PATH/$PROJECT_NAME/db/sqlalchemy/migrate_repo/versions/001_${PROJECT_NAME}_init.py
rm -r $PROJECT_PATH/$PROJECT_NAME/db/sqlalchemy/migrate_repo/versions/001_\<project_name\>_init.py

# Generate manager
if [ "$MANAGER_NAME" = "" ]; then
    rm -r $PROJECT_PATH/$PROJECT_NAME/\<manager_service_name\>
    rm -r $PROJECT_PATH/$PROJECT_NAME/cmd/\<manager_service_name\>.py
else
    # Set first char of MANAGER_NAME upper
    MANAGER_NAME_C=`echo $MANAGER_NAME|sed 's/^\(.\)/\U\1/g'`
    # Rename \<manager_service_name\> with MANAGER_NAME
    cp -r $PROJECT_PATH/$PROJECT_NAME/\<manager_service_name\> \
     $PROJECT_PATH/$PROJECT_NAME/$MANAGER_NAME
    rm -r $PROJECT_PATH/$PROJECT_NAME/\<manager_service_name\>
    cp -r $PROJECT_PATH/$PROJECT_NAME/cmd/\<manager_service_name\>.py \
     $PROJECT_PATH/$PROJECT_NAME/cmd/${MANAGER_NAME}.py
    rm -r $PROJECT_PATH/$PROJECT_NAME/cmd/\<manager_service_name\>.py
    manager_files="$PROJECT_NAME/*.py
$PROJECT_NAME/*/*.py
$PROJECT_NAME/*/*/*.py
$PROJECT_NAME/*/*/*/*.py
$PROJECT_NAME/*/*/*/*/*.py"
    replace_file "$manager_files" "<manager_service_name>" "$MANAGER_NAME"

    Manager_files="$PROJECT_NAME/*/*.py
$PROJECT_NAME/*/*/*.py"
    replace_file "$Manager_files" "<Manager_service_name>" "$MANAGER_NAME_C"
fi

echo "Generate project $PROJECT_NAME successful."
