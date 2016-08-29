#!/usr/bin/env bash

CHECKONLY=0
if [ "$1" == "--checkonly" ]; then
    CHECKONLY=1
fi

PROJECT_NAME=${PROJECT_NAME:-<project_name>}
CFGFILE_NAME=${PROJECT_NAME}.conf.sample


TEMPDIR=`mktemp -d /tmp/${PROJECT_NAME}.XXXXXX`
trap "rm -rf $TEMPDIR" EXIT

tools/config/generate_sample.sh from_tox

if [ -e etc/${PROJECT_NAME}/${CFGFILE_NAME} ]; then
    CFGFILE=etc/${PROJECT_NAME}/${CFGFILE_NAME}
elif [ -e <project_name>/opts.py]; then
    echo -en "\n\nWARNING: Found <project_name>/opts.py file. \n"
    echo -en "Check for generate_<project_name>_opts.py failure.\n\n"
    exit 1
else
    echo "${0##*/}: Can't find config file."
    exit 1
fi
