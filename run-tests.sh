#!/bin/bash

# Change to directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "=============="
echo "CHECKING STYLE"
echo "=============="
echo

flake8 --ignore=E501 . | grep -v -e ./kitabu/tests/__init__.py -e ./kitabu/tests/settings.py -e ./spa/settings_local.py

warnings_status=$?

if [ $warnings_status -eq 1 ]; then
    echo "No style warnings"  # zero lines (grep exit status 1) means no warnings
fi

echo 
echo "============="
echo "RUNNING TESTS"
echo "============="
echo

./manage.py test kitabu
