# Joringels integrates your stand alone web-services to a virtual cluster
This package is in alpha, so it will contain bugs and be limited in its functionality.

Joringels is a light weight remote function call (RPC) tool, that uses REST data (json string) to transmit commands and kwargs to the specified target machine. Joringels on the target machine then uses the received command and its associated kwargs to perform a local function call. The result is then send back to the calling machine.
All commands and services are available from any machine belonging to the same designated joringels cluster. 

A joringels cluster is defined as:

    a. multiple machines with each running joringels
    b. who share the same dataKey and dataSafeKey
    c. who share the same cluster parameter file
    d. whos client IP address has been added to the allowedClients list inside the cluster parameter file


<img src="https://drive.google.com/uc?id=1CKnOpDYizxTmIVRmaUckiaUWj9hEdUF1" alt="joringels_cluster" class="plain" height="300px" width="500px">

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
    # this assumes you have a adder package served by joringels with a func at api=0 that
    # performs an addition of the kwargs provided
    # def add(*args, a, b, **kwargs):
    #    return a + b
    data = {'api': 0, 'kwargs':{'a': 5 'b': 5 }
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
    jo load -n dataSafeName -pd productName -cl clusterName
```

### serve your api access point
```
    jo serve -n dataSafeName -con packageToServe -cn clusterName -rt -t

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
- jo dockerize \[-y\] \[--hard\] (-y will docker run, --hard will docker build)
- docker exec -it jo bash

NOTE: get 'jo info' to be GREEN before running dockerize


## 7 Known issues
- data ClusterParams dataclass keeps adding ips to allowedClients for every call
```
    # defaults used for startup sequence
    decPrefix: decrypted_
    port: pick a port
    validator: text_is_valid
    secureHosts:
    - Computername1
    - Computername2
```
