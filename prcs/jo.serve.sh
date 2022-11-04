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


SAFENAME=$1
CONNECTOR=$2
source /etc/environment

# get application parameter
# APPPATH=`(jq -r ".$SAFENAME|.[1]" $AVAILABLEREPOS)`
# apiEndpointsPath=$apiEndpointDir/$SAFENAME/api_endpoints/params.yml


# # set datasafe
# if [ "$SAFENAME" == "digiserver" ]
# then
#     # get server parameter
#     CONNECTOR='joringels'
# else
#     TEMPSAFENAME=$SAFENAME
#     CONNECTOR='application'
#     # host and port come from api_endpoints/params.yml
# fi

cd $JORINGELSPATH
pipenv run jo serve -n $SAFENAME -con $CONNECTOR -rt
