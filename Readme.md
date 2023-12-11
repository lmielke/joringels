# Joringels manages your rest api calls (RPC calls) to connected machines.
This package is in alpha, so it will contain bugs and be limited in its functionality.

Joringels is a light weight remote function call (RPC) toll. Jorinels turns your stand alone python package into a cluster of fully functioning web-services. Joringels uses REST data (json string) to transmit an api-id and kwargs to a target server machine. The target machine then uses the kwargs to perform a function call. The result is then send back to the calling machine.

Joringels combines multiple web-services into one single cluster (i.e. a web-server, a database and a mail server). Joringels will then serve all cluster web-services (web-services that share the same dataSafe) to a single network. Think of a cluster as multiple container instances inside a docker compose file.

NOTE: Joringels does not serialize python objects. For that you might look for more complex packages like google rpc.


<img src="https://drive.google.com/uc?id=1CIS09n1chfoNAgEJWSiWx3WqfcVP2Wtb" alt="joringels_thumb_from_gpt" class="plain" height="300px" width="500px">

<small><small>Unaltered generated image to honor our future ai overloards.</small></small>

### run in Shell
jo action [-n safeName] -e entryName # (actions: load, upload, fetch, serve, call)
```
    # Examples
    # getting parameter data from joringels
    jo fetch -e parameterKey [-ip targetHost] [-p targetPort]
    # serving joringels
    jo serve -n saveName -con joringels -cn testing -rt -t
    # loading a datasafe from kdbx source to .ssp folder
    jo load -n oamailer -src application, jo load -n mydatasafe -src kdbx
    # calling a remote api
    jo call -a apiIndex -con targetApplication -e kwargs

```
## Installation
Install joringels inside the package environment for the package which you want to serve as a microservice.

Recommended install:
Copy the Pipfile from joringels.docker to your install folder.
Alternatively clone the repo and use the Pipfile from joringels package directory (directory where the setup.py file lives)
```
    # enter your package folder then run the following
    pipenv install
    pipenv shell
    jo info
```

NOTE: joringels is available on pypi, however it contains one dependency package 'logunittest'
which currently is NOT available on pypi. You have to manually install it to use joringels.

## After install Setup
0. setup environment variables (see below)
1. create a \~/.ssp directory (this will contain any en/decrpyted files)
2. maintain your secrets in a kdbx file (i.e. passwords.kdbx)
3. create a dataSafe with jo load -n safeName -pd product -cl cluster -src kdbx

### 0. Environment variables (mandatory)
#### Mandatory environment variables:
- secrets: path to your secrets source (i.e. kdbx file)
- DATAKEY: password to your encrypted secrets values (inner encryption only dict values)
- DATASAFEKEY: password to your encrypted secrets (outer encryption for REST data)
- DATASAFENAME: default name of your dataSafe
- DATASAFEIP: ip address of your dataSafe server (if joringels microservice is used)

#### Optional environment variables:
- secrets: path to your local secrets file (i.e. passwords.kdbx secrets hosting machine)
- DATASAFEPORT: if not provided sts.defaultPort is used or derrived from cluster params
- NODEMASTERIP: if not provided soc.get_local_ip() is used


# API Endpoint use
## Example of a mail application server (oamailer) on port 7007:
This example hosts a mail application server as a microservice. A connected client machine can call the oamailer.mail.send(\*\*kwargs) method. Calling method and kwargs are send via encrypted json data. The target machine (oamailer) then uses decrypted kwargs to compose and send the mail.

### 1. API INIT (commands to setup server and client)
```
    # Upload aip-endpoint to server (oamailer)
    jo load -n oamailer -src application
    
    # Serve aip-endpoint NOTE: -p port parameter is not accepted
    jo serve -n saveName -con joringels -cn testing -rt -t
    jo serve -n saveName -con oamailer -cn testing -rt -t

    # Test availability aip-endpoint
    jo fetch -e apiEndpointDir -n oamailer -ip 192.168.0.174 -p 7007
    jo fetch -e 0 -n oamailer -ip 192.168.0.174 -p 7007

    # Test correctness of aip-endpoint
    jo fetch -e logunittest -n oamailer -ip 192.168.0.174 -p 7007

    # Run api-endpoint
    jo call 

```

### 2. API CALL to running API
API uses the joringels.src.actions.call module to call the oamailer API. This is then pushed
to jorinde.py, which creates the post request to the target machine.

Here is a code example for calling a remote server.

```python

    import os, sys, socket
    from joringels.src.actions import call
    print(sys.executable)
    """
    Remove linebreaks and indents and try this command
    jo call         -a 0 -con oamailer
                    -e "{
                    'sendTo': 'yourMail@gmail.com', 
                    'subject': 'hello from test', 
                    'text': 'Hello World!,\\nThis is a testmail from WHILE-AI-2'}" 
    """
    # runs a remote server micro-service using api id and kwargs
    data = {   
            'api': 0,
            'kwargs':{
                    'a': 5
                    'b': 5
            }
    call.main(connector='adder', data=data)
    # out 10
```


### create a API access Point inside oamailer package (yaml file)
Here is a param file example for the target machine (joringels server machine).

```yml
    # appPath is needed for app import
    # possible actions to be performed with default parameters
    # steps
    # jo load -pr oamailer -src application -con '...\oamailer\joringels\params.json'
    
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
    jo load -pr oamailer -src application -con '...\oamailer\joringels\params.json'
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
- see install instructions above

## 3 Setup
### secret host machine setup (mandatory)
- install password manager # Currently only keepass is supported !
You have to setup two keepass entries specific to joringels:
    - 'dataSafe': 'pwd' (encrypts safeName.json file when it is saved-locally or scp-send)
    - 'cluster': contains cluster parameters for the cluster where joringels is working in
#### KDBX setup
- create a kdbx file (i.e. passwords.kdbx) and add a group named data_safes)
- create one or multiple entries within the data_safes group
- Inside the 'advanced' tab create a attachment 'safe_params.yml'

##### safe_params.yml
tbd

### secret host machine setup (optional)
- define some helpful environment variables to avoid typing kwargs all the time
    - DATASAFEIP: ip the host server uses to serve secrets (ipv4 address of your server)
    - DATASAFENAME: name of dataSafe you want to use in a network


### Joringels package setup (mandatory)
- create a  \~/.ssp directory (this will contain any en/decrpyted files)
- in keepass add Group -> name it like settings.py / groupName (i.e. joringels_data_safes)
- in keepass, inside the Group create a dataSafe entry (i.e. myfirstdatasafe) with generated password

- for each dataSafe create a soures/targets .json file as shown in example below
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
- remove the unprotected .json files, so they only exist in kdbx now

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