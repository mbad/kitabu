#!/bin/bash

# Change to directory of this script
BASE_DIRECTORY="$(cd  $(dirname "${BASH_SOURCE[0]}"); pwd)"
cd $BASE_DIRECTORY

CHECK_STYLE=1

for i
do
    if [ $i = '-s' ]
    then
        CHECK_STYLE=0
    fi
done

if [ $CHECK_STYLE -gt 0 ]
then
    echo "=============="
    echo "CHECKING STYLE"
    echo "=============="
    echo

    flake8 --ignore=E501 . | grep -v -e kitabu/tests/__init__.py -e kitabu/tests/settings.py -e spa/settings_*

    warnings_status=$?

    if [ $warnings_status -eq 1 ]; then
        echo "No style warnings"  # zero lines (grep exit status 1) means no warnings
    fi
else
    echo "=================="
    echo "NOT CHECKING STYLE"
    echo "=================="
    echo
fi


echo
echo "============="
echo "RUNNING TESTS"
echo "============="
echo 

django-admin.py test kitabu --settings='kitabu.tests.settings' --pythonpath="$BASE_DIRECTORY"
