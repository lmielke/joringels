# info.py
import joringels.src.settings as sts
import subprocess
import os, sys
import configparser

import colorama as color

color.init()


def main(*args, **kwargs):
    print(f"""\n{f" JORINGELS USER info ":#^80}""")
    print("Simple tool for managing your secrets in a semi secure way.")
    print(f"\nsample {kwargs = }\n")
    msg = f"\nGo through steps in Readme.md ! Then use the following shell cmds"
    print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
    print(f"{f' Usage info ':#^80}")
    print(f"example: joringels upload -n digiserver -src kdbx -con scp [-ip limit_target]\n")
    print("\nactions")
    msg = (
        f"upload / upload_all: extract kdbx kdb secrets and upload to server:\n"
        f"\t\t-n, safeName: name of data safe, i.e. [kdbx -> joringels_data_sefe/] digiserver\n"
        f"\t\t-src, source: location of data safe, i.e. kdbx\n"
        f"\t\t-con, connector: method to connect to server, i.e. scp\n\n"
        f"\t\t-ip, host: limit upload to one of the safe targets, interrupts upload\n\n"
        f"unprotectedload: extract kdbx secrets and save them to .ssp dir\n"
        f"\texample: joringels unprotectedload -n digiserver -src kdbx [-ip limit_target]\n\n"
        f"load: extract kdbx secrets and save encrypted result to .ssp dir\n"
        f"\texample: joringels load -n digiserver -src kdbx [-ip limit_target]\n\n"
        f"fetch: read secrets into your application\n"
        f"\texample: joringels fetch -n digi_postgres_login\n"
        f"\t\t-e, entryName: name of secret, i.e. in kdbx its the name of your entry\n\n"
        f"serve: via http to all apps inside your local network\n"
        f"\texample: joringels serve -n digiserver -k myextrasecurepassword -rt\n"
        f"\t\t-e, entryName: name of secret, i.e. in kdbx its the name of your entry"
    )
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
    print(
        f"to see available kdbx entries: python -m joringels.src.sources.kdbx show -s path/to/sources"
    )
    warning = f"\t\tNOTE: This is NOT a secure socket! ONLY USE IN LOCAL NETWORK!\n"
    print(f"{color.Fore.RED}{warning}{color.Style.RESET_ALL}")

    # developer info
    print(f"{f' Developer info ':#^80}\n")
    subprocess.call(["tree", sts.srcPath], shell=True)
    msg = f" <-- runs the program by importing and executing joringels/src/actions/module.py\n"
    print("|---__main__.py", f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
    print(f"\njoringels/src/actions/... modules can be used as examples how to run")
    print(
        f"running via shell is identical to directly launching an action joringels/src/actions/... "
    )
    msg = (
        f"\t-n, safeName: string used by source such as kdbx.py\n"
        f"\t-src, source: string which actions/module.py uses to import the source adapter\n"
        f"\t-con, connector: string which actions/module.py uses to import coonnection adapter\n"
        f"\t-ip, host: string used as a filter of target list"
    )
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")


if __name__ == "__main__":
    main()
