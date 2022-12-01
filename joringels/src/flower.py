# flower.py
import json, re, time, yaml, cgi
from urllib.parse import unquote
from http.server import BaseHTTPRequestHandler, HTTPServer
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.logger as logger
import joringels.src.get_soc as soc
from datetime import datetime as dt
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
        self.host, self.port = agent.AF_INET
        msg = f"\nNow serving http://{self.host}:{self.port}/ping"
        logger.log(__name__, msg, *args, verbose=agent.verbose, **kwargs)

    def __call__(self, *args, **kwargs):
        """Handle a request."""
        super().__init__(*args, **kwargs)

    def do_GET(self):
        requestedItem = unquote(self.path.strip("/"))
        allowedClients = sts.appParams.get(sts.allowedClients)
        if not auth_checker.authorize_client(allowedClients, self.client_address[0]):
            returnCode, msg = 403, f"\nfrom: {self.client_address[0]}, Not authorized!"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)

        if requestedItem == "ping":
            returnCode = 200
            responseTime = re.sub(r"([:. ])", r"-", str(dt.now()))
            response = bytes(json.dumps(f"OK {responseTime}\n"), "utf-8")

        else:
            found = self.agent._from_memory(requestedItem, None)

            if found is None:
                returnCode, msg = (
                    404,
                    f"\nfrom {self.client_address[0]}, Not found! {requestedItem}",
                )
                logger.log(__name__, f"{returnCode}: {msg}")
                time.sleep(5)
                self.send_error(returnCode, message=msg)

            else:
                returnCode = 200
                response = bytes(json.dumps(found), "utf-8")

        if returnCode in [200]:
            self.send_response(returnCode)
            self.send_header("Content-type", f"{requestedItem}:json")
            self.send_header("Content-Disposition", "testVal")
            self.end_headers()
            self.wfile.write(response)

    def do_POST(self):
        requestedItem = unquote(self.path.strip("/"))
        ctype, pdict = cgi.parse_header(self.headers.get("content-type"))
        allowedClients = sts.appParams.get(sts.allowedClients)
        if not auth_checker.authorize_client(allowedClients, self.client_address[0]):
            returnCode, msg = 403, f"\nfrom: {self.client_address[0]}, Not authorized!"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)

        payload = self.rfile.read(int(self.headers.get("Content-Length"))).decode("utf-8")
        # call to application
        response = self.agent._invoke_application(payload, requestedItem)

        if response is None:
            returnCode, msg = 404, f"{self.client_address[0]}, Not found! {requestedItem}"
            logger.log(__name__, f"{returnCode}: {msg}")
            time.sleep(5)
            self.send_error(returnCode, message=msg)
        else:
            returnCode = 200
            response = bytes(json.dumps(response), "utf-8")

        if returnCode in [200]:
            self.send_response(returnCode)
            self.send_header("Content-type", f"{requestedItem}/json")
            self.send_header("Content-Disposition", "testVal")
            self.end_headers()
            self.wfile.write(response)
