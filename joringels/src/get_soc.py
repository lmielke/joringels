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


def get_allowed_hosts(*args, **kwargs):
    allowedHosts = sts.appParams.get("allowedHosts")
    if get_hostname() in sts.appParams.get("secureHosts"):
        allowedHosts.append(get_ip())
    return allowedHosts


def host_info(*args, host=False, port=False, **kwargs):
    host = host if host else get_ip()
    port = port if port else sts.appParams.get("secretsPort")
    return host, port
