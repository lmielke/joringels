import os
from itertools import count
from dataclasses import dataclass, field
from typing import List, Dict, Any
import joringels.src.settings as sts
import joringels.src.get_soc as soc
import joringels.src.arguments as arguments


@dataclass
class DataSafe:
    safeName: str = None
    safeIp: str = None
    safePort: int = None
    dataKey: str = None
    dataSafeKey: str = None
    entries: List[str] = field(default_factory=list)

    def __post_init__(self, *args, **kwargs):
        if not self.safeName:
            self.safeName = os.environ.get("DATASAFENAME")
        if not self.safeIp:
            self.safeIp = os.environ.get("DATASAFEIP", soc.get_local_ip())
        if not self.safePort:
            self.safePort = os.environ.get("DATASAFEPORT", sts.defaultPort)
        if not self.dataKey:
            self.dataKey = os.getenv("DATAKEY", "default_datakey")
        if not self.dataSafeKey:
            self.dataSafeKey = os.getenv("DATASAFEKEY", "default_datasafekey")
        if not self.entries:
            self.entries = []
        # Type checking
        self._validate_fields()

    def _validate_fields(self):
        if not isinstance(self.safeName, str):
            raise TypeError(f"Expected 'safeName' to be a str, got {type(self.safeName).__name__}")
        if not isinstance(self.safeIp, str):
            raise TypeError(f"Expected 'safeIp' to be a str, got {type(self.safeIp).__name__}")
        if not isinstance(self.dataKey, str):
            raise TypeError(f"Expected 'dataKey' to be a str, got {type(self.dataKey).__name__}")
        if not isinstance(self.dataSafeKey, str):
            raise TypeError(
                f"Expected 'dataSafeKey' to be a str, got {type(self.dataSafeKey).__name__}"
            )
        if not all(isinstance(entry, str) for entry in self.entries):
            raise TypeError("All 'entries' must be of type str")

    @classmethod
    def source_kdbx(cls, kwargs: Dict[str, Any]):
        # Extract data from the kwargs dictionary
        safeName = kwargs.get("title", "")
        safeIp = kwargs.get("safeIp", "")
        safePort = kwargs.get("safeIp", "")
        dataKey = kwargs.get("username", "")
        dataSafeKey = kwargs.get("password", "")
        entries = kwargs.get("safe_params", {}).get("entries", {})

        # Create a new instance of DataSafe with the extracted data
        return cls(safeName, safeIp, safePort, dataKey, dataSafeKey, entries)

    def source_kwargs(self, kwargs: Dict[str, Any]):
        # Extract data from the kwargs dictionary
        if kwargs.get("safeName") is not None:
            self.safeName = kwargs.get("safeName")
        if kwargs.get("safeIp") is not None:
            self.safeIp = kwargs.get("safeIp")
        if kwargs.get("dataKey") is not None:
            self.dataKey = kwargs.get("dataKey")
        if kwargs.get("dataSafeKey") is not None:
            self.dataSafeKey = kwargs.get("dataSafeKey")

    def source_secrets(self, secrets: Dict[str, Any], connector):
        # Extract data from the secrets dictionary (part of cluster params)
        self.entries = secrets.get(self.safeName)["safe_params"]["entries"]

    def source_cluster(self, clusterParams: Dict[str, Any], connector):
        # Extract data from the clusterParams dictionary (part of cluster params)
        pass


@dataclass
class ClusterParams:
    nodeMasterIp: str = None
    secureHosts: List[str] = field(default_factory=list)
    allowedClients: List[str] = field(default_factory=list)
    network: str = None
    host: str = None
    port: int = None
    portMapping: str = None
    services: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.nodeMasterIp:
            self.nodeMasterIp = os.environ.get("NODEMASTERIP", soc.get_local_ip())
        if not self.secureHosts:
            self.secureHosts = [soc.get_local_ip()]
        if not self.allowedClients:
            self.allowedClients = [soc.get_local_ip()]
        if not self.network:
            self.network = ""
        if not self.host:
            self.host = soc.get_local_ip()
        if not self.port:
            self.port = sts.defaultPort
        if not self.portMapping:
            self.portMapping = f"{str(self.port)}:{str(self.port)}"
        self._validate_fields()

    def _validate_fields(self):
        if not all(isinstance(secureHost, str) for secureHost in self.secureHosts):
            raise TypeError("All 'secureHosts' must be of type str")
        if not all(isinstance(allowedClient, str) for allowedClient in self.allowedClients):
            raise TypeError("All 'allowedClients' must be of type str")
        if not isinstance(self.network, str):
            raise TypeError(f"Expected 'network' to be an str, got {type(self.network).__name__}")
        if not isinstance(self.host, str):
            raise TypeError(f"Expected 'host' to be an str, got {type(self.host).__name__}")
        if not isinstance(self.port, int):
            raise TypeError(f"Expected 'port' to be an int, got {type(self.port).__name__}")
        if not isinstance(self.portMapping, str):
            raise TypeError(
                f"Expected 'portMapping' to be an str, got {type(self.portMapping).__name__}"
            )
        if not isinstance(self.nodeMasterIp, str):
            raise TypeError(
                f"Expected 'nodeMasterIp' to be an str, got {type(self.nodeMasterIp).__name__}"
            )

    def source_kwargs(self, kwargs: Dict[str, Any]):
        # Extract data from the kwargs dictionary
        self.secureHosts.extend(kwargs.get("secureHosts"))
        self.allowedClients.extend(kwargs.get("allowedClients"))
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")

    def source_services(self, services: Dict[str, Any], connector):
        # Extract data from the services dictionary (part of cluster params)
        self.secureHosts.extend(soc.update_secure_hosts())
        self.allowedClients.extend(soc.update_allowed_clients(services))
        self.network = services.get(connector).get("networks")
        self.host = soc.get_local_ip()
        self.port = int(services.get(connector).get("ports")[0].split(":")[0])
        self.portMapping = f"{str(self.port)}:{str(self.port)}"
        self.services.update(services["services"])

    def source_cl_params(self, clParams: Dict[str, Any], connector):
        # Extract data from the clParams dictionary (part of cluster params)
        self.nodeMasterIp = clParams.get("NODEMASTERIP", self.nodeMasterIp)

    def update(self, kwargs: Dict[str, Any]):
        self.__dict__.update(kwargs)


@dataclass
class apiParams:
    connector: str = None
    api: Dict[int, dict] = field(default_factory=dict)

    def __post_init__(self):
        if self.api:
            self.api = {int(k) if str(k).isnumeric() else k: v for k, v in self.api.items()}
        self._validate_fields()

    def _validate_fields(self):
        if not all(isinstance(connector, str) for connector in self.connector):
            raise TypeError("All 'connector' must be of type str")
        if not all(isinstance(ix, int) for ix, ap in self.api.items()):
            raise TypeError("All 'api indecies' must be of type int")
