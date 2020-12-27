#!/bin/bash

export IS_MAINTENANCE_SCHEDULED=$1
if (( $# > 1 ))
then
  export MAINTENANCE_START_DATETIME=$2
else
  export MAINTENANCE_END_DATETIME=$3
fi
