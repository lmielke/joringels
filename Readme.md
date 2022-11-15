# Joringels manages your rest api access points to remote applications.

## up next
Topics to be implemented:
- integrate .kdbx file in ressources

### run in Shell
jo action [-n safeName] -e entryName # (actions: load, upload, fetch, serve, invoke)
```
    # Examples
    jo load -n oamailer -src application, jo load -n mydatasafe -src kdbx
    jo fetch -e _joringel.yml
    # load to local docker export dir
    jo upload -src kdbx -con docker -pr joringels -n digiserver -pd wobbles -c testing
    # load to remote server
    jo upload -src kdbx -con scp -pr joringels -n digiserver -pd wobbles -c testing

```
## Installation
```
    pipenv install joringels
    # now follow setup steps further down

```

# API Endpoint use
## Example mail application oamailer on port 7007:

### 1. API INIT
```
    # Upload aip-endpoint (change to loadloc script)
    jo load -n oamailer -src application
    
    # Serve aip-endpoint NOTE: -p port parameter is not accepted
    jo serve -n digiserver -con oamailer -rt

    # Test availability aip-endpoint
    jo fetch -e apiEndpointDir -n oamailer -ip 192.168.0.174 -p 7007
    jo fetch -e 0 -n oamailer -ip 192.168.0.174 -p 7007

    # Run api-endpoint
    jo invoke 

```

### 2. API CALL
API uses the joringels.src.actions.invoke module to call the API. This is then pushed
to jorinde.py, which creates the post request to the target machine.

```python
    # jo.py 09_05_2022__17_35_20
    # python C:\Users\lars\python_venvs\utils\experimental\09_05_2022__17_35_20_jo.py

    import os, sys
    from joringels.src.actions import invoke
    print(sys.executable)

    # runs a remote server micro-service
    payload = {   
            'api': 0,
            'payload':{
                    'sendTo': 'mysamplemail@gmail.com', 
                    'subject': f"hello from jo.py {__file__}",
                    'text': f"Hello World!,\nThis is a testmail from {os.environ['COMPUTERNAME']}"},
            }

    # define oamailer parmeter
    kwargs = {
            'apiName': 'oamailer',
            'connector': 'application',
            'data': payload,
            'host': 'localhost',
            'port': 7007,
    }
    print(f"jo.file: {kwargs = }")
    params = invoke.api(**kwargs, retain=True)
```


### create a API access Point inside oamailer package (yaml file)
```yml
    # appPath is needed for app import
    # possible actions to be performed with default parameters
    # steps
    # jo load -pr oamailer -src application -con '...\oamailer\joringels\params.yml'
    
    projectName: oamailer
    contentType: application/oamailer
    projectDir: ~/python_venvs/modules/oamailer
    port: 7007
    # define one numeric entry for every api (0: send, 1: read ...)
    0:
      
      # NOTE: below import is used like importlib.import_module(api['import'], projectName)
      #       so prjectName.import should result in oamailer.actions.send
      
      import: .actions.send
      action: send
      response: null

    1:
      import: .actions.read
        ...
```
### load the yaml file to joringels
```
    jo load -pr oamailer -src application -con '...\oamailer\joringels\params.yml'
```

### serve your api access point
```
    jo serve -n oamailer -rt -p 7007 -pr oamailer

```



### use in Python
```
    from joringels.src.actions import fetch
    # using retain=False (default is False) will delete dataSafe in .ssp folder
    creds = fetch.alloc(safeName='mysafeName', entryName='myentryName', retain=True)
```
- NOTE: this is in alpha
- NOTE: holds password in environment variables (only use if env vars are safe)
- NOTE: Joringels assumes, that your source and target VMs are un-compromized.
- NOTE: ONLY serve secrets via http inside a protected local network

# Important develoment info
- Currently kdbx (password-manager) is the only supported secret source
- scp is used as connector for secrets file transfer to server



## 1 What joringels does
- efficiently manage your secrets while maintaining it in a save location i.e. kdbx
- create dataSafes (bundles of secrets) using combined entries in your source (i.e. kdbx)
- serve dataSafes secrets to a single network
    - source ~/.ssp directory serves secrets to a single client
    - source encrypted http connection serves secrets to multiple clients simultaneously
- extracts and uploads your encrypted dataSafes to multiple remote server simultaneously

## 2 Download and install from gitlab
- python3.9 +
- git clone https://gitlab.com/larsmielke2/joringels.git

### Install using repo Pipfile (NOTE: handle install issues as described in pt 7 !)
- pipenv install (NOTE: this installs joringels as editable, change Pipfile if needed)

## 3 Setup
### secret host machine setup (mandatory)
- install password manager # Currently only keepass is supported !
- define some neccessary password environment variables
    - 'yourSafeName': 'pwd' (encrypts safeName.yml file when it is saved-locally or scp-send)
    - JORINGELS: 'pwd' (encrypts http secrets NOTE: must be equal on server and all clients)

### secret host machine setup (optional)
- define some helpful environment variables to avoid typing kwargs all the time
    - DATASAFEIP: ip the host server uses to serve secrets (ipv4 address of your server)
    - DATASAFENAME: name of dataSafe you want to use in a network
    - DATASAFEROLE: server or client
    - JORINGELSPATH: full path to where the Pipfile lives


### Joringels package setup (mandatory)
- create a  \~/.ssp directory (this will contain any en/decrpyted files)
- in keepass add Group -> name it like settings.py / groupName (i.e. joringels_data_safes)
- in keepass, inside the Group create a dataSafe entry (i.e. myfirstdatasafe) with generated password

- for each dataSafe create a soures/targets .yml file as shown in example below
- NOTE: targets AND entries contain full paths to keepass entries
````
    # entries for single or multiple target server logins (server using the dataSafe secrets)
    targets:
      - pyenvs/provider/droplets/testing/github-runner-token
    
    # entries for secrets your dataSafe will hold
    entries:
      - pyenvs/utils/dbs/my_db_login
      - pyenvs/provider/apiTokens/repo_download
      - pyenvs/provider/apiTokens/myprovider_api_token
      - pyenvs/provider/google_oauth
````
- attach the new file to your dataSafe entry (myfirstdatasafe): keepass>>advanced>>attach
- also attach the following \_joringels.yml (runtime parameters) file in the same dataSafe as above
```
    # only these hosts are allowed to request a secret
    allowedClients:
        - 164.92.206.169
        - 188.166.87.121
    application: joringels
    decPrefix: decrypted_
    kPath: fullPath to your .kdbx file
    lastUpdate: 2022-06-06-11-22-21-842103
    port: 7000
    validator: text_is_valid
    # name of allowed develoment systems
    secureHosts:
        - BLUE-MOON_1
        - BLUE-MOON_2
```
- remove the unprotected .yml files, so they only exist in kdbx now

### Joringels setup (optional)
- if you wish, change relevant names and dirs in joringels/src/settings.py


### Try the folowing commands
1. jo info: (will show you more readme)
2. jo load: -n safeName (will load your dataSafe secrets file to .ssh)
3. jo chkey -n safeName [-nk os] # not needed but propaply better to do so
4. jo serve -n safeName

## 5 Some Windows gimmics
### powershell functions to add to your $PROFILE
#### fjo
```
    function FJO($entry){
        $curr = $PWD
        cd $env:JORINGELSPATH
        pipenv run jo fetch -e $entry
        cd $curr
    }
```
- jo.serve from Windows start menu: copy joringels/prcs/jo.serve shortcut to startmenu
- then run like: fjo entryname

#### loadloc
```
    function loadloc(){
        $curr = $PWD
        cd $env:JORINGELSPATH
        pipenv run jo load -n $env:DATASAFENAME -src $env:secrets
        pipenv run jo chkey -n $env:DATASAFENAME -nk os
        cd $curr
    }
```

## 6 Some docker stuff
- docker container is under construction
- to run use
    - docker run -itd --rm --name [joringels] -p [7000:7000] -w /home/gitlab-runner/your_env_name/joringels --network [illuminati] joringels bash ./prcs/jo.serve.sh


## 7 Known issues
- as of 06/2022 python10.5 not installing (use python10.4 instead)
- FileNotFoundError: [Errno 2] No such file or directory <- create folder/file as shown below
.virtualenvs\\[your_env_name]\\lib\\site-packages\\joringels\\resources\\\_joringels.yml
```
    # defaults used for startup sequence
    decPrefix: decrypted_
    port: pick a port
    validator: text_is_valid
    secureHosts:
    - Computername1
    - Computername2
```

FileNotFoundError: [Errno 2] No such file or directory  <- create empty folder as shown below
.virtualenvs\\[your_env_name]\\lib\\site-packages\\joringels\\logs
