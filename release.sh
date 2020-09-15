#!/usr/bin/env sh

rm dist/*
python setup.py sdist bdist_wheel
python -m twine upload --repository inf-lvs-dataset-loader dist/*
