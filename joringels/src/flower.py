# flower.py
import json, re, time, yaml
from urllib.parse import unquote
from http.server import BaseHTTPRequestHandler, HTTPServer
import joringels.src.settings as sts
import joringels.src.logger as logger
import joringels.src.get_soc as soc
from datetime import datetime as dt
from joringels.src.encryption_dict_handler import text_encrypt
import joringels.src.auth_checker as auth_checker


class MagicFlower(BaseHTTPRequestHandler):
    def __init__(self, agent, *args, **kwargs):
        self.agent = agent
        timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))
        self.flowerLog = logger.mk_logger(
            sts.logDir,
            f"{timeStamp}_{__name__}.log",
            __name__,
        )
        self.host, self.port = soc.host_info(**kwargs)
        msg = f"\nNow serving http://{self.host}:{self.port}/ping"
        logger.log(__name__, msg, *args, verbose=agent.verbose, **kwargs)

    def __call__(self, *args, **kwargs):
        """Handle a request."""
        super().__init__(*args, **kwargs)

    def do_GET(self):
        safeItem = unquote(self.path.strip("/"))
        allowedClients = self.agent.secrets.get(sts.appParamsFileName).get('allowedClients')
        if not auth_checker.authorize_client(allowedClients, self.client_address[0]):
            returnCode, msg = 403, f"\nfrom: {self.client_address[0]}, Not authorized!"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)

        elif safeItem == "ping":
            returnCode = 200
            responseTime = re.sub(r"([:. ])", r"-", str(dt.now()))
            response = bytes(json.dumps(f"OK {responseTime}"), "utf-8")

        elif not self.agent.secrets.get(safeItem):
            returnCode, msg = 404, f"\nfrom {self.client_address[0]}, Not found! {safeItem}"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)

        else:
            found = self.agent.secrets.get(safeItem, None)
            encrypted = {k: text_encrypt(yaml.dump(vs)) for k, vs in found.items()}
            returnCode = 200
            response = bytes(json.dumps(encrypted), "utf-8")

        if returnCode in [200]:
            self.send_response(returnCode)
            self.send_header("Content-type", f"{safeItem}:json")
            self.send_header("Content-Disposition", "testVal")
            self.end_headers()
            self.wfile.write(response)
