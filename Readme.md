# Joringels manages your secrets across multiple VMs.
- NOTE: Joringels assumes, that your source and target VMs are un-compromized.
- NOTE: ONLY serve secrets via http inside a protected local network
- Currently kdbx (password-manager) is the only supported secret source

## 1 What joringels does
- serve data_safes to a single target system using decrypted files (usually dev environment)
    - joringels uses a .ssp directory next to your .ssh directory to manage secrets
- serve data_safes to multiple instances simultaneously using local http socket
- efficiently manage your secrets while maintaining it in a save location i.e. kdbx
- create data_safes (bundles of secrets) using combined entries in your secret source
- extract and upload your data_safes as encrpyted files to multiple server simultaneously

## 2 Download and install
python3.9 +
### Download
- git clone https://gitlab.com/larsmielke2/joringels.git
- you might want to: git remote rm origin

### Install inside existing environment
- pipenv shell (activate your target environment)
- cd joringels
- pipenv install . or pipenv install -e .

### Install using repo Pipfile
- cd joringels
- pipenv install



## 3 Set-up on your development machine

### If you want, adjust joringels/src/settings.py
- set all relevant names and dirs (only upper section of settings.py)
- you can leave these parameters unchanged

### General setup (mandatory)
- creta a \~/.ssp directory (this will contain any en/decrpyted files)
- install a secret source (currently kdbx is supported)

### Adjust the ressources/joringels.yml file to your needs (mandatory)
- copy the file to a directry of your choice
- adjust allowed hosts (hosts that can access your secrets via http)
- adjust secure server hosts (hosts that can hold decrypted secret files or serve via http)

### Adjust the ressources/safe_params.yml file to your needs (mandatory)
- copy the file to a directory of your choice
- define entries that your data_safe contains (i.e. kdbx entries of secrets)
- define targets your data_safe is served to (i.e. kdbx entries of servers)

### Create as data_safe in i.e. kdbx
- open kdbx
- create a new group called like settings.safeName i.e. 'joringels_data_safe'
- add a new entry, example: (title: mydigiserver, pwd: my_safe_secrets_encryption_password)
- go to advanced tab and add joringels.yml and safe_params.yml
- safe your entry and veryfy the files are properly attached
- remove the unprotected .yml files, so they only exist in kdbx now

### Try the folowing commands
- 'joringels info', (will show you more readme)
- try the cmds as shown there

## 4 What is a data_safe
- a data_safe is a bundle of secrets comprizing of multiple secret entries
- a data_safe may contain all sorts of secret / semi-secret information, not only user, pwd
- each server instance uses one single data_safe to gain authorized access to its ressources
- a secret is only referenced to the data_safe, which allows seemless updates and distribution
- however, if a secret is updated it needs to be actively re-distributed via its data_safes

## 5 Known issues
- as of 06/2022 python10.5 not installing (use python10.4 instead)