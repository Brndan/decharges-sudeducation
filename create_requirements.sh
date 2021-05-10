#!/usr/bin/env bash

set -euo pipefail

echo "pip-compile -U -o requirements.txt ..."
pip-compile -U -o requirements.txt

echo "pip-compile -U -o requirements-tests.txt ..."
python -c "from distutils.core import run_setup ; dist = run_setup('setup.py') ; print('\n'.join(dist.tests_require))" > requirements.in
pip-compile -U -o requirements-tests.txt
rm requirements.in

