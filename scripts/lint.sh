#!/bin/bash

ruff check --output-format=github .
ruff format --check .