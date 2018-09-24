#!/usr/bin/env bash
# clean-up distribution from various derived files
# usually it is not needed

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${script_dir}

for del_dir in akrr.egg-info build .coverage .pytest_cache shippable etc log
do
    if [ -d "${del_dir}" ]; then
        rm -rf ${del_dir}
    fi
done

find . -name '__pycache__' -type d -exec rm -r "{}" \;

find . -name '*.pyc' -type f -delete

rm ./tests/.coverage
rm ./tests/regtest1/.crontmp
rm ./.coverage

