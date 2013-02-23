#!/bin/bash

# Change to directory of this script
BASE_DIRECTORY="$(cd  $(dirname "${BASH_SOURCE[0]}"); pwd)"
cd $BASE_DIRECTORY

echo "=============="
echo "CHECKING STYLE"
echo "=============="
echo

flake8 --ignore=E501 . | grep -v -e kitabu/tests/__init__.py -e kitabu/tests/settings.py -e spa/settings_local.py

warnings_status=$?

if [ $warnings_status -eq 1 ]; then
    echo "No style warnings"  # zero lines (grep exit status 1) means no warnings
fi

echo
echo "============="
echo "RUNNING TESTS"
echo "============="
echo 

django-admin.py test kitabu --settings='kitabu.tests.settings' --pythonpath="$BASE_DIRECTORY"
