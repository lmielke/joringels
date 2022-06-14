# Joringels manages your secrets across multiple VMs.
## NOTE: Joringels assumes, that your source and target VMs are un-compromized.
## NOTE: ONLY serve secrets via http inside a protected local network

## What joringels does
- serve data_safes to single instance as decrypted files or to multiple instances as local http socket
- NOTE: joringels will create a .ssp directory next to your .ssh directory to manage secrets
- manage and maintain your secrets in a save location i.e. keepass
- create data_safes (bundles of secrets) using combined entries in your secret source
- extract and upload your data_safes as encrpyted files to multiple server simultaneously

## Download and install
NOTE: python3.9 and higher
### Download
- git clone https://gitlab.com/larsmielke2/joringels.git
- you might want to: git remote rm origin

### Install in existing environment
- cd joringels
- pipenv shell (activate your target environment)
- pipenv install .

### Install using repo Pipfile
- cd joringels
- pipenv install



# Set-up
## if you want, adjust joringels/src/settings.py
- set all relevant names and dirs
- you can also leave these parameters unchanged

## mandatory: adjust the ressources/joringels.yml file to your needs
- copy the file to a directry of your choice
- adjust allowed hosts (hosts that can access your secrets via http)
- adjust secure server hosts (hosts that can hold decrypted secret files or serve via http)

## mandatory: adjust the ressources/safe_params.yml file to your needs
- copy the file to a directory of your choice
- define entries that your data_safe contains (i.e. keepass entries of secrets)
- define targets your data_safe is served to (i.e. keepass entries of servers)

## Create as data_safe in i.e. keepass
- open keepass
- create a new group called like settings.kpsGrpName i.e. 'joringels_data_safe'
- add a new entry, example: (title: mydigiserver, pwd: my_safe_secrets_encryption_password)
- go to advanced tab and add joringels.yml and safe_params.yml
- safe your entry and veryfy the files are properly attached
- remove the unprotected .yml files, so they only exist in keepass now

## Try the folowing commands
- 'joringels info', (will show you more readme)
- try the cmds as shown there

## Known issues
- as of 06/2022 python 10.5 not installing (use 10.4 instead)