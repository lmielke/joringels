# logger.py
import os, re
import logging
from datetime import datetime as dt

import joringels.src.settings as sts


def mk_logger(logDir, fileName, loggerName, *args, **kwargs):
    # logging config to put somewhere before calling functions
    # call like: logger.debug(f"logtext: {anyvar}")
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.INFO)
    logformat = "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s"
    datefmt = "%m-%d %H:%M"
    logForm = logging.Formatter(fmt=logformat, datefmt=datefmt)
    logPath = os.path.join(logDir, fileName)
    logHandler = logging.FileHandler(logPath, mode="a")
    logHandler.setFormatter(logForm)
    logger.addHandler(logHandler)
    return logger


def log(name, msg, *args, verbose=0, **kwargs):
    timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))
    if verbose >= 1:
        print(msg)
    log = mk_logger(sts.logDir, f"{timeStamp}_{name}.log", name)
    log.info(msg)
