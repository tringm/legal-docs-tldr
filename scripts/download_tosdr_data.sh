#!/bin/bash

function usage {
  echo "usage: $(basename "$0") [target_directory]

  download tosdr.org services rating data to the target_directory
  "
}

if [[ "$1" == "" ]]
then
  echo
  echo "error: missing target_directory"
  echo
  usage
  exit 1
fi

if [ -d $1 ]
then
  git clone https://github.com/tosdr/tosdr.org.git "$1"
  echo "removing all except the api folder"
  find "$1" -maxdepth 1 ! -wholename "$1/api" ! -wholename "$1" -exec rm -rf {} \;
  echo "extracting all json files except all.json"
  find "$1/api" -name "*.json" ! -name "all.json" -exec mv {} "$1" \; && rm -rf "$1/api"
else
  echo "error: target_directory $1 does not exist"
  usage
fi