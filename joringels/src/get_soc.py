# get_soc.py -> import joringels.src.get_soc as soc
import os, re, requests, socket
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.logger as logger


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    socName = s.getsockname()[0]
    return socName


def get_external_ip_from_env():
    ip_address = os.environ.get("my_ip", None)
    if ip_address is None:
        ip_address = get_external_ip()
    return ip_address


def get_external_ip():
    try:
        r = requests.get("https://api.ipify.org")
        if r.status_code == 200:
            return r.text
    except:
        return None


def get_hostname():
    return socket.gethostname().upper()


def get_allowed_clients(*args, **kwargs):
    allowedClients = sts.appParams.get(sts.allowedClients)
    if get_hostname() in sts.appParams.get(sts.secureHosts):
        allowedClients.append(get_local_ip())
    return allowedClients


def derrive_host(*args, connector: str = None, **kwargs):
    """
    if host is None, try to derrive it from other params
    """
    # joringels case allowes to fall back to os.environ["DATASAFEIP"]
    if connector == sts.appName or connector is None:
        host = os.environ["DATASAFEIP"]
    # this is the api case, where host can be derrived using the connector (i.e. oamailer)
    elif connector is not None:
        host = connector
    return host


def resolve_host_alias(*args, host, connector: str = None, **kwargs):
    if host == "localhost":
        host = get_local_ip()
    elif host == sts.appName:
        host = os.environ["DATASAFEIP"]
    elif host.startswith(sts.devHost) and host[-1].isnumeric():
        host = socket.gethostbyname(f"{host}")
    elif host.isnumeric():
        domain, host = os.environ.get("NETWORK"), int(host)
        if domain.startswith(sts.devHost) and host in range(10):
            host = socket.gethostbyname(f"{domain}{host}")
    elif host == connector and os.name == 'nt':
        host = get_local_ip()
    return host


def get_ip(apiParams=None, *args, host=None, connector: str = None, **kwargs):
    if connector is None:
        connector = sts.appName
    # on a server host and port need to be read from service params
    network = list(apiParams[connector].get("networks").keys())[0]
    host = apiParams[connector].get("networks")[network].get("ipv4_address")
    return host


def get_port(apiParams=None, *args, port=None, connector: str = None, **kwargs):
    if port is not None: return int(port)
    if connector is None or connector == sts.appName: return sts.defaultPort
    # on a server host and port need to be read from service params
    if apiParams is None: apiParams = get_api_params(*args, connector=connector, **kwargs)
    port = int(port) if port else int(apiParams[connector].get("ports")[0].split(":")[0])
    return port

def get_api_params(*args, clusterName, connector, **kwargs):
    params = {'entryName': clusterName, 'retain': True}
    from joringels.src.actions import fetch
    apiParams = fetch.alloc(*args, **params)['cluster_params']['services']
    return apiParams


def get_host(*args, host=None, **kwargs):
    isIp = r"\d{1,3}\.\d{1,3}\.\d{1,3}"
    if host is None:
        host = derrive_host(*args, **kwargs)
    if not re.search(isIp, host):
        host = resolve_host_alias(*args, host=host, **kwargs)
    if not re.search(isIp, host):
        host = get_ip(*args, host=host, **kwargs)
    return host
