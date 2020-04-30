#!/bin/bash

DOWNLOAD_DIR=data/tosdr_services

function check_at_top {
  if [[ ! -f legal_docs_tldr/__init__.py ]]; then
    echo
    echo "error: this script must be run from the project directory"
    echo
    exit 1
  fi
}

function download_and_extract {
  echo "downloading tosdr.org services rating data to $DOWNLOAD_DIR"
  git clone https://github.com/tosdr/tosdr.org.git "$DOWNLOAD_DIR"
  echo "removing all except the api folder"
  find "$DOWNLOAD_DIR" -maxdepth 1 ! -wholename "$DOWNLOAD_DIR/api" ! -wholename "$DOWNLOAD_DIR" -exec rm -rf {} \;
  echo "extracting all json files except all.json"
  find "$DOWNLOAD_DIR/api" -name "*.json" ! -name "all.json" -exec mv {} "$DOWNLOAD_DIR" \; && rm -rf "$DOWNLOAD_DIR/api"
}

check_at_top
if [ ! -d $DOWNLOAD_DIR ]
then
  mkdir -p $DOWNLOAD_DIR
fi
download_and_extract