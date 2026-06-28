#!/bin/sh
# Create sample.zip from sample/ directory
set -e
if [ ! -d "sample" ]; then
  echo "sample/ directory not found"
  exit 1
fi
zip -r sample.zip sample/
ls -lh sample.zip
