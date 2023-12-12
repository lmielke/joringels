# jo dockerize

Quickly transfer this app into a running docker container using 'jo dockerize'. For more details read the Dockerfile and Pipfile.

## What it does.
There is a action in joringels.actions named dockerize. When you run it using 'jo dockerize'
it will build a docker image for your app named 'joringels'. 
1. dockerize will ask for confirmation to rebuild the 'joringels' image.
2. if you confirm, the image will be rebuild
3. dockerize will copy the dataSafe you specify from .ssp to joringels.docker (default is env:DATASAFENAME)
4. Dockerfile will COPY the Pipfile & dataSafe into the images joringels package directory
5. Dockerfile bulid will install your Pipfile including joringels using pipenv (there will be NO specific cloning from git..., NOTE: joringels is implicitly cloned during install)
5. dockerize will output a docker run string, which you can copy and immediately run from
    inside the joringels package. (package directory where the setup.py file lives)
6. the locally copied dataSafe should be deleted automatically after install from joringels.docker. However, check to be sure!

## How to use
- activate joringels environemnt
- jo dockerize \[-y\] \[--hard\] # --hard docker build, -y docker run
- follow instructions and read the presented install cmds carefully
- in case you did not use -y, copy paste 'docker run ...' output from install output (stay inside package directory)

## Enter the container
- docker exec -it jo bash
This will direct you to the joringels package directory and activate the environemnt. You can then run:
- jo info
- pipenv run serve

### Test locally using:
- jo fetch -e logunittest (shoud output 0 tests because its not a package)

### Test remotely using:
- jo fetch -e logunittest -p 7000
- curl http://localhost:7000/ping

### Removes
NOTE: docker is run using --rm, so the container should be removed if stopped. Howerver, you can use:
- docker rm jo
- docker rmi joringels

### Parameters
Parameters are taken from cluster_params from the dataSafe as well as os.environ. You can overwrite the dataSafe if required. use -n safeName