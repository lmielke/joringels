# get_soc.py -> import joringels.src.get_soc as soc

import os, requests, socket
import joringels.src.settings as sts


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    socName = s.getsockname()[0]
    return socName

def get_external_ip_from_env():
    ip_address = os.environ.get('my_ip', None)
    if ip_address is None:
        ip_address = get_external_ip()
    return ip_address

def get_external_ip():
    try:
        r = requests.get('https://api.ipify.org')
        if r.status_code == 200:
            return r.text
    except:
        return None


def get_hostname():
    return socket.gethostname().upper()


def get_allowed_clients(*args, **kwargs):
    allowedClients = sts.appParams.get(sts.allowedClients)
    if get_hostname() in sts.appParams.get(sts.secureHosts):
        allowedClients.append(get_ip())
    return allowedClients

def resolve(host, *args, **kwargs):
    if host is None:
        return host
    elif host == 'localhost':
        host = get_ip()
    elif host.isnumeric():
        domain, host = os.environ.get('NETWORK'), int(host)
        if domain.startswith(sts.devHost) and host in range(10):
            host = socket.gethostbyname(f"{domain}{host}")
    elif host.startswith(sts.devHost) and host[-1].isnumeric():
        host = socket.gethostbyname(f"{host}")
    elif host.startswith('joringels'):
        host = os.environ['DATASAFEIP']
    return host

def host_info_extended(secrets, *args, connector, host=None, port=None, **kwargs):
    if connector in ['joringels']:
        host = host if host else get_ip()
        port = port if port else sts.defaultPort
    elif connector:
        host = secrets[sts.clusters_params][sts.apiParamsFileName][connector].get('HOST')
        port = secrets[sts.clusters_params][sts.apiParamsFileName][connector].get('PORT')
    else:
        pass
    host = resolve(host)
    return host, port