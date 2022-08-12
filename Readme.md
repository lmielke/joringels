# Joringels manages your secrets across multiple VMs.
- NOTE: holds password in environment variables (only use if env vars are safe)
- NOTE: Joringels assumes, that your source and target VMs are un-compromized.
- NOTE: ONLY serve secrets via http inside a protected local network

# Important def info
- Currently kdbx (password-manager) is the only supported secret source




## 1 What joringels does
- serve dataSafes secrets to a single network
    - dev network: joringels uses a ~/.ssp directory to host secrets
    - linux web-server network: joringels serves secrets using encrypted http connection
- serve dataSafes to multiple clients simultaneously using local http socket
- efficiently manage your secrets while maintaining it in a save location i.e. kdbx
- create dataSafes (bundles of secrets) using combined entries in your secret source
- extracts and uploads your encrypted dataSafes to multiple remote server simultaneously

## 2 Download and install
- python3.9 +
- git clone https://gitlab.com/larsmielke2/joringels.git

### Install using repo Pipfile
- cd joringels (top folder where the Pipfile lives)
- pipenv install

### run in Shell
```
    jo action [-n safeName] -e entryName # actions: load, upload, fetch, serve
```

### use in Python
```
    from joringels.src.actions import fetch
    # using retain=False (default is False) will delete dataSafe in .ssp folder
    creds = fetch.alloc(safeName='mysafeName', entryName='myentryName', retain=True)
```

### development system setup (mandatory)
- install password manager # Currently only keepass is supported !
- define some helpful environment variables
    - yourSafeName: 'pwd' (used to encrypt decrypt secrets)

### development system setup (optional)
- define some helpful environment variables
    - DATASAFEIP: ip the host server uses to serve secrets (ipv4 address of your server)
    - DATASAFENAME: name of dataSafe you want to use in a network
    - DATASAFEROLE: server (serve and consume), client (consume only)


### Joringels setup (mandatory)
- create a  \~/.ssp directory (this will contain any en/decrpyted files)
- in keepass add Group -> name it like settings.py / groupName
- in keepass create a dataSafe entry inside the Group (i.e. myfirstdatasafe)

- create a soures/targets yml file
- file example
````
    targets:
      - pyenvs/provider/droplets/testing/github-runner-token
    entries:
      - pyenvs/utils/dbs/my_db_login
      - pyenvs/provider/apiTokens/repo_download
      - pyenvs/provider/apiTokens/myprovider_api_token
      - pyenvs/provider/google_oauth
````
- attach the yaml file to your dataSafe entry (myfirstdatasafe): keepass>>advanced>>attach
- also attach \_joringels.yml file in the same was as above
```
    # only these hosts are allowed to request a secret
    allowedHosts:
        - 164.92.206.169
        - 188.166.87.121
    application: joringels
    decPrefix: decrypted_
    kPath: /Users/Lars/OneDrive/Dokumente/50 sonstiges/aktuell_2021.kdbx
    lastUpdate: 2022-06-06-11-22-21-842103
    secretsPort: 7000
    validator: text_is_valid
    # name of allowed develoment systems
    secureHosts:
        - BLUE-MOON_1
        - BLUE-MOON_2
```



### Joringels setup (optional)
- if you whish, change relevant names and dirs in joringels/src/settings.py


### Create as data_safe in i.e. kdbx
- open kdbx
- create a new group called like settings.safeName i.e. 'joringels_data_safe'
- add a new entry, example: (title: mydigiserver, pwd: my_safe_secrets_encryption_password)
- go to advanced tab and add \_joringels.yml and safe_params.yml
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
- however, if a secret is updated it needs to be actively re-distributed via its dataSafes

## 5 Some Windows gimmics
- run jo.serve from Windows start menu: copy joringels/prcs/jo.serve shortcut to startmenu
- powershell function to add to your $PROFILE
- then run like: JO entryname
```
    function JO($SECRET){
        $out = curl "http://$($env:DATASAFEIP):7000/$SECRET"
        return $out
    }
```

## 6 Some docker stuff
- docker container is under construction
- to run use
    - docker run -itd --rm --name [joringels] -p [7000:7000] -w /home/gitlab-runner/python_venvs/libraries/joringels --network [illuminati] joringels bash ./prcs/jo.serve.sh


## 7 Known issues
- as of 06/2022 python10.5 not installing (use python10.4 instead)