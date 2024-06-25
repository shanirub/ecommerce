#!/bin/bash

# Run pylint on Python files excluding migrations

find . -type f -name "*.py" ! -path "*/migrations/*" -exec pylint --output-format=colorized {} +

