# flower.py
import json, re, time
from urllib.parse import unquote
from http.server import BaseHTTPRequestHandler, HTTPServer
import joringels.src.settings as sts
import joringels.src.logger as logger
import joringels.src.get_soc as soc
from datetime import datetime as dt


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
        logger.log(__name__, msg, *args, **kwargs)
        self.allowedHosts = soc.get_allowed_hosts(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Handle a request."""
        super().__init__(*args, **kwargs)

    def do_GET(self):
        client = unquote(self.path.strip("/"))
        if not (self.client_address[0] in self.allowedHosts):
            returnCode, msg = 403, f"\nfrom: {self.client_address[0]}, Not authorized!"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)

        elif client == "ping":
            returnCode = 200
            responseTime = re.sub(r"([:. ])", r"-", str(dt.now()))
            response = bytes(json.dumps(f"OK {responseTime}"), "utf-8")

        elif not self.agent.secrets.get(client):
            returnCode, msg = 404, f"\nfrom {self.client_address[0]}, Not found! {client}"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)

        else:
            found = self.agent.secrets.get(client, None)
            returnCode = 200
            response = bytes(json.dumps(found), "utf-8")

        if returnCode in [200]:
            self.send_response(returnCode)
            self.send_header("Content-type", f"{client}:json")
            self.send_header("Content-Disposition", "testVal")
            self.end_headers()
            self.wfile.write(response)
