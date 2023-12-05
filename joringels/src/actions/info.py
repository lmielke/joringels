# info.py
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.joringels
import subprocess
import os, sys
import configparser

import colorama as color

color.init()
COL_RM = color.Style.RESET_ALL
YELLOW = color.Fore.YELLOW
GREEN = color.Fore.GREEN
RED = color.Fore.RED
WHITE = color.Fore.WHITE


def main(*args, **kwargs):
    msg = f"""\n{f" {sts.appName.upper()} USER info ":#^80}"""
    print(f"{GREEN}{msg}{COL_RM}")
    # check dataSafes
    msg = f"\nChecking dataSafes in {sts.encryptDir}..."
    print(f"{WHITE}{msg}{COL_RM}")
    safes = os.listdir(sts.encryptDir)
    if not safes:
        print(f"{YELLOW}No dataSafe found in {sts.encryptDir}{COL_RM}")
    else:
        for ds in safes:
            if os.path.splitext(ds)[-1] == sts.fext:
                print(f"{YELLOW}\t{ds} -> not encrypted{COL_RM}")
            else:
                print(f"{GREEN}\t{ds}{COL_RM}")
    # check secret keys
    msg = f"\nChecking keys in os.environ..."
    print(f"{WHITE}{msg}{COL_RM}")
    for name in ("DATASAFEKEY", "DATAKEY"):
        if os.environ.get(name) is None:
            print(f"\t{RED}Environment variable {name} not set!{COL_RM}")
        else:
            print(f"\t{GREEN}Environment variable {name} set{COL_RM}")
    # check other env Vars
    msg = f"\nChecking safe params in os.environ..."
    print(f"{WHITE}{msg}{COL_RM}")
    for name in ("DATASAFEIP", "DATASAFENAME"):
        if os.environ.get(name) is None:
            print(f"\t{RED}Environment variable {name} not set!{COL_RM}")
        else:
            print(f"\t{GREEN}Environment variable {name} set{COL_RM}")


if __name__ == "__main__":
    main()
