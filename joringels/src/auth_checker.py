# auth_check.py


import yaml, os, re
import colorama as color

color.init()
from time import sleep

import joringels.src.settings as sts
import joringels.src.get_soc as soc


def authorize_client(clients, authIp=None, *args, **kwargs):
    if authIp is None:
        authIp = soc.get_ip()
    for ip in clients:
        if authIp == ip:
            # print(f"authIp == ip: {authIp} == {ip}")
            return True
        elif ip.endswith("*") and authIp.startswith(ip[:-1]):
            return True
    # print(f"authIp != ip: {authIp} != {ip}")
    return False


def authorize_host(authIp=None, *args, **kwargs):
    if authIp is None:
        authIp = soc.get_ip()
    if (
        authIp in sts.appParams[sts.secureHosts]
        or soc.get_hostname() in sts.appParams[sts.secureHosts]
    ):
        # print(f"authIp in secureHosts: {authIp} in {sts.appParams[sts.secureHosts]}")
        return True
    # print(f"authIp not in secureHosts: {authIp} not in {sts.appParams[sts.secureHosts]}")
    return False
