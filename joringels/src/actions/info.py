# info.py
import joringels.src.settings as sts

import os, sys
import configparser

parser = configparser.ConfigParser()
parser.read(os.path.join(sts.appBasePath, "setup.cfg"))

import colorama as color

color.init()


def main(*args, **kwargs):
    print(f"""{f" JORINGELS VERSION {parser.get('metadata', 'version')} ":#^80}""")
    print("Simple tool for managing your secrets in a semi secure way.")
    print(f"\nsample {kwargs = }\n")
    msg = f'\nGo through steps in Readme.md ! Then use the following shell cmds'
    print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
    msg = (
        f"upload: extract keepass kdb secrets and upload to server:\n"
        f"\texample: joringels upload -g digiserver -src keepass -con scp [-ip limit_target]\n"
        f"\t\t-g, groupName: name of data safe, i.e. [keepass -> joringels_data_sefe/] digiserver\n"
        f"\t\t-src, source: location of data safe, i.e. keepass\n"
        f"\t\t-con, connector: method to connect to server, i.e. scp\n\n"
        f"\t\t-ip, host: limit upload to one of the safe targets, interrupts upload\n\n"
        f"unprotectedload: extract keepass secrets and save them to .ssp dir\n"
        f"\texample: joringels unprotectedload -g digiserver -src keepass [-ip limit_target]\n\n"
        f"load: extract keepass secrets and save encrypted result to .ssp dir\n"
        f"\texample: joringels load -g digiserver -src keepass [-ip limit_target]\n\n"
        f"fetch: read secrets into your application\n"
        f"\texample: joringels fetch -c digi_postgres_login\n"
        f"\t\t-c, client: name of secret, i.e. in keepass its the name of your entry\n\n"
        f"serve: via http to all apps inside your local network\n"
        f"\texample: joringels serve -g digiserver -k 58039C1E5E9EF20D2D52F0A9D17E931A -rt\n"
        f"\t\t-c, client: name of secret, i.e. in keepass its the name of your entry"
    )
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")

    warning = f"\t\tNOTE: This is NOT a secure socket! ONLY USE IN LOCAL NETWORK!\n"
    print(f"{color.Fore.RED}{warning}{color.Style.RESET_ALL}")
