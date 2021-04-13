#!/usr/bin/env bash

set -euo pipefail

echo "pip-compile -o requirements.txt ..."
pip-compile -o requirements.txt

echo "pip-compile -o requirements-tests.txt.tmp ..."
python -c "from distutils.core import run_setup ; dist = run_setup('setup.py') ; print('\n'.join(dist.tests_require))" | pip-compile -o requirements-tests.txt.tmp -

echo "Generating real requirements-tests.txt file ..."
echo '-r requirements.txt' | cat - requirements-tests.txt.tmp > requirements-tests.txt
rm requirements-tests.txt.tmp
