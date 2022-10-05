# contracts.py
import joringels.src.settings as sts
import os, sys
import colorama as color

color.init()


def checks(*args, **kwargs):
    kwargs = error_check_params(*args, **kwargs)
    error_upload_all(*args, **kwargs)
    kwargs = warn_deletion(*args, **kwargs)
    kwargs["source"] = sts.unalias_path(kwargs["source"])
    return kwargs


def warn_deletion(*args, retain, hard, **kwargs):
    if kwargs["action"] == "serve":
        if retain == False and hard == False:
            msg = f"Retain is set to {retain}. Your secrets.yml will be deleted after reading !"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            y = input("To continue type [Y]: ")
            if y == "Y":
                kwargs["retain"] = False
                return kwargs
            else:
                msg = f"Interrupt by user intervention: {kwargs}"
                exitMsg = f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}"
                raise Exception(exitMsg)
        else:
            kwargs["retain"] = True
            return kwargs
    else:
        kwargs["retain"] = True
        msg = f"NON deleting action {kwargs['action']}!"
        print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
        return kwargs


def error_upload_all(action, *args, host, **kwargs):
    if action != "fetch" and host is not None:
        msg = f"Your -ip, host contains {host}. It must be empty to use load_all!"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        exit()

def error_check_params(*args, action, source, connector, **kwargs):
    # check actions
    actionsPath = os.path.join(sts.settingsPath, 'actions')
    actions = [p[:-3] for p in os.listdir(actionsPath) if p.endswith('.py') and p != '__init__.py']
    if not action in actions:
        msg = f"\ninvalid action '{action}'! Available actions: {actions}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return None
    else:
        kwargs['action'] = action

    # check source
    actionsPath = os.path.join(sts.settingsPath, 'connectors')
    connectors = [p[:-3] for p in os.listdir(actionsPath) if p.endswith('.py') and p != '__init__.py']
    if not connector in connectors:
        msg = f"\ninvalid connector '{connector}'! Available connectors: {connectors}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return None
    else:
        kwargs['connector'] = connector

    # check source
    actionsPath = os.path.join(sts.settingsPath, 'sources')
    sources = [p[:-3] for p in os.listdir(actionsPath) if p.endswith('.py') and p != '__init__.py']
    if not any([source.endswith(src) for src in sources]):
        msg = f"\ninvalid source '{source}'! Available sources: {sources}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return None
    else:
        kwargs['source'] = source

    return kwargs