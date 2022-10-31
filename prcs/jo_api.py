# jo.py 09_05_2022__17_35_20
# python C:\Users\lars\python_venvs\utils\experimental\09_05_2022__17_35_20_jo.py

import os, sys, time
from joringels.src.actions import invoke
print(sys.executable)


def main(api, data, *args, **kwargs):
    # call your api like this
    params = invoke.api(*args, apiName=api, data=data, host='1', **kwargs, retain=True)


if __name__ == '__main__':
    # payload depends on the tpye of api application
    data = {   
            'api': 0,
            'payload':{
            'sendTo': 'larsmielke2@gmail.com', 
            'subject': f"hello from {os.path.basename(__file__)}",
            'text': f"Hello World!,\nThis is a testmail from {os.environ['COMPUTERNAME']}"},
    }

    # relvant arguments to call oamailer api
    # NOTE: kwargs have to be loaded for server AND client
    # mailerParams = {
    #                 'safeName': 'oamailer',
    #                 'contentType': 'application/json',
    #                 'host': 'localhost',
    #                 'port': 7007,
    # }
    main('oamailer', data)