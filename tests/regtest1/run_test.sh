#!/usr/bin/env bash

# do not exit if any command fails for the initialization
# it will be reset before tests
set +e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd ${script_dir}

# find akrr and akrrregtest
which_akrr=$(which akrr 2> /dev/null)

if [ ! -x "${which_akrr}" ] ; then
    echo "Can not find akrr executable, should be in PATH"
    exit 1
fi

which_akrrregtest=$(which akrrregtest 2> /dev/null)

if [ ! -x "${which_akrrregtest}" ] ; then
    which_akrrregtest=$(readlink -e ../bin/akrrregtest)
fi

if [ ! -x "${which_akrrregtest}" ] ; then
    echo "Can not find akrr executable, should be in PATH"
    exit 1
fi

echo "akrr to use: ${which_akrr}"
echo "akrrregtest to use: ${which_akrrregtest}"

#exit if any command fails
set -e

for var in "$@"
do
    case "$var" in
    setup)
        echo "Launching AKRR setup"
        ${which_akrrregtest} setup
        ;;
    resource)
        echo "Launching AKRR resource adding "
        ${which_akrrregtest} resource
        ;;
    *)
        echo "Unknown option $var"
        exit 1
        ;;
    esac
done



