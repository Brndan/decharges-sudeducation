#!/usr/bin/env bash
dirs=$(find decharges/ -maxdepth 1 -type d -not -name "decharges" -not -name ".*" -not -name "__*" -not -name "docker*" -not -name "locale" -not -name "static")

isort $dirs decharges/urls.py
flake8 $dirs decharges/urls.py
black $dirs decharges/urls.py
