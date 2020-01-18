#!/usr/bin/env bash

pytest --cov=erika tests/ --cov-report=html --html=test_output/report.html -m 'not hardware'
