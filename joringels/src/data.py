from dataclasses import dataclass, field
from typing import List, Dict, Any
import joringels.src.settings as sts
import joringels.src.get_soc as soc


@dataclass
class DataSafe:
    safeName: str
    dataKey: str = None
    dataSafeKey: str = None
    entries: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.dataKey:
            self.dataKey = os.getenv("DATAKEY", "default_datakey")
        if not self.dataSafeKey:
            self.dataSafeKey = os.getenv("DATASAFEKEY", "default_datasafekey")
        # Type checking
        self._validate_fields()

    def _validate_fields(self):
        if not isinstance(self.safeName, str):
            raise TypeError(f"Expected 'safeName' to be a str, got {type(self.safeName).__name__}")
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
        dataKey = kwargs.get("username", "")
        dataSafeKey = kwargs.get("password", "")
        entries = kwargs.get("safe_params", {}).get("entries", [])

        # Create a new instance of DataSafe with the extracted data
        return cls(safeName, dataKey, dataSafeKey, entries)


@dataclass
class AppParams:
    secureHosts: List[str] = field(default_factory=list)
    allowedClients: List[str] = field(default_factory=list)
    host: str = None
    port: int = None
    network: str = None
    portMapping: str = None

    def __post_init__(self):
        if not self.secureHosts:
            self.secureHosts = [soc.get_local_ip()]
        if not self.allowedClients:
            self.allowedClients = [soc.get_local_ip()]
        if not self.host:
            self.host = soc.get_local_ip()
        if not self.port:
            self.port = sts.defaultPort
        if not self.network:
            self.network = ""
        if not self.portMapping:
            self.portMapping = f"{str(self.port)}:{str(self.port)}"
        self._validate_fields()

    def _validate_fields(self):
        if not all(isinstance(host, str) for host in self.secureHosts):
            raise TypeError("All 'secureHosts' must be of type str")
        if not all(isinstance(client, str) for client in self.allowedClients):
            raise TypeError("All 'allowedClients' must be of type str")
        if not isinstance(self.host, str):
            raise TypeError(f"Expected 'host' to be an str, got {type(self.host).__name__}")
        if not isinstance(self.port, int):
            raise TypeError(f"Expected 'port' to be an int, got {type(self.port).__name__}")
        if not isinstance(self.network, str):
            raise TypeError(f"Expected 'network' to be an str, got {type(self.network).__name__}")
        if not isinstance(self.portMapping, str):
            raise TypeError(
                f"Expected 'portMapping' to be an str, got {type(self.portMapping).__name__}"
            )

    @classmethod
    def source_settings(cls):
        # Extract data from the kwargs dictionary
        secureHosts = [soc.get_local_ip()]
        allowedClients = [soc.get_local_ip()]
        host = sts.defaultHost
        port = sts.defaultPort
        cls(secureHosts, allowedClients, host, port)
        return cls

    @classmethod
    def source_kwargs(cls, kwargs: Dict[str, Any]):
        # Extract data from the kwargs dictionary
        secureHosts = kwargs.get("secureHosts")
        allowedClients = kwargs.get("allowedClients")
        host = kwargs.get("host")
        port = kwargs.get("port")
        return cls(secureHosts, allowedClients, host, port)

    def source_services(self, services: Dict[str, Any], connector):
        # Extract data from the services dictionary (part of cluster params)
        self.secureHosts = soc.update_secure_hosts()
        self.allowedClients = soc.update_allowed_clients(services)
        self.host = soc.get_local_ip()
        self.port = int(services.get(connector).get("ports")[0].split(":")[0])
        self.network = services.get(connector).get("networks")
        self.portMapping = f"{str(self.port)}:{str(self.port)}"

    def update(self, kwargs: Dict[str, Any]):
        self.__dict__.update(kwargs)
