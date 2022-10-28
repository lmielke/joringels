# get_soc.py -> import joringels.src.get_soc as soc

import os, socket
import joringels.src.settings as sts


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    socName = s.getsockname()[0]
    return socName


def get_hostname():
    return socket.gethostname().upper()


def get_allowed_clients(*args, **kwargs):
    allowedClients = sts.appParams.get("allowedClients")
    if get_hostname() in sts.appParams.get("secureHosts"):
        allowedClients.append(get_ip())
    return allowedClients

def resolve(*args, host, **kwargs):
    if host == 'localhost':
        host = get_ip()
    return host

def host_info_extended(jor, *args, **kwargs):
    if jor.connector == 'application':
        AF_INET = (resolve(host=jor.host), jor.port)
    else:
        AF_INET = host_info(*args, **kwargs)
    return AF_INET


def host_info(*args, host=False, port=False, **kwargs):
    host = host if host else get_ip()
    port = port if port else sts.appParams.get("port")
    return host, port
