# info.py
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.joringels
import subprocess
import os, sys
import configparser

import colorama as color

color.init()


def main(*args, **kwargs):
    msg = f"""\n{f" {sts.appName.upper()} USER info ":#^80}"""
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
    with open(os.path.join(sts.appBasePath, "setup.cfg"), "r") as f:
        info = f.read()
    print(f"info: \n{info}")

    print(f"sessions: {joringels.src.joringels.Joringel.sessions}")


if __name__ == "__main__":
    main()
