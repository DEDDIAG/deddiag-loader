#!/usr/bin/env sh

rm dist/*
python setup.py sdist bdist_wheel
python -m twine upload dist/*
