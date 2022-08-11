#!/bin/bash
# jo.serve.sh

source /etc/environment
cd /home/$USERNAME/python_venvs/libraries/joringels
pipenv run jo serve -n digiserver -rt