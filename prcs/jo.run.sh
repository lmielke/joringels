#!/bin/bash

# Regular Colors
BLACK="\[\033[0;30m\]"        # Black
RED="\[\033[0;31m\]"          # Red
GREEN="\[\033[0;32m\]"        # Green
YEL="\[\033[0;33m\]"       # Yellow
BLUE="\[\033[0;34m\]"         # Blue
PURPLE="\[\033[0;35m\]"       # Purple
CYAN="\[\033[0;36m\]"         # Cyan
WHITE="\[\033[0;37m\]"        # White
NC='\033[0m' # No Color


ACTION=$1
APPNAME=$2
CONNECTOR=$3
source /etc/environment

# get application parameter
APPPATH=`(jq -r ".$APPNAME|.[1]" $AVAILABLEREPOS)`
# apiEndpointsPath=$apiEndpointDir/$APPNAME/api_endpoints/params.yml


# set datasafe
if [ "${CONNECTOR}" -eq 'application' ]
then
    TEMPSAFENAME=$DATASAFENAME
else
    TEMPSAFENAME=$APPNAME
    # host and port come from api_endpoints/params.yml
fi

cd $APPPATH
pipenv run jo $ACTION -n $TEMPSAFENAME -con $CONNECTOR -rt
