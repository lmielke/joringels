# contracts.py
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import os, sys
import colorama as color

color.init()


def checks(*args, **kwargs):
    check_serve(*args, **kwargs)
    kwargs = error_check_params(*args, **kwargs)
    error_upload_all(*args, **kwargs)
    kwargs = warn_deletion(*args, **kwargs)
    check_secrets_path(*args, **kwargs)
    return kwargs


def check_secrets_path(*args, **kwargs):
    if os.name == "nt":
        secretsPath = sts.unalias_path(os.environ.get("secrets"))
        # assert that secretsPath is actually a path that does exist
        msg = f"{color.Fore.RED}secretsPath: {secretsPath} not valid!{color.Style.RESET_ALL}"
        assert os.path.exists(secretsPath), msg


def check_serve(*args, host=None, port=None, connector=None, **kwargs):
    errors = {}
    if host is not None:
        errors["host"] = f"serve host must be provided in api params file but is {host}"
    if port is not None and port != 7000:
        errors["port"] = f"serve port must only be provided in api params file but is {port}"
    if connector == "application" and errors:
        msg = f"{color.Fore.RED}contracts.check_serve.ERROR, {errors}{color.Style.RESET_ALL}"
        raise Exception(msg)


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
    if action not in ["fetch", "invoke", "serve"] and host is not None:
        msg = f"Your -ip, host contains {host}. It must be empty to use load_all!"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        exit()


def error_check_params(*args, action, source, connector, **kwargs):
    # check actions
    actionsPath = os.path.join(sts.settingsPath, "actions")
    actions = [
        p[:-3]
        for p in os.listdir(actionsPath)
        if p.endswith(".py") and p != "__init__.py" and p != "tempfile.py"
    ]
    if not action in actions:
        msg = f"\ninvalid action '{action}'! Available actions: {actions}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return None
    else:
        kwargs["action"] = action

    # check source
    if source == "application":
        pass

    # checking connectors
    connectorPath = os.path.join(sts.settingsPath, "connectors")
    connectors = {"scp", "oamailer", "joringels", "docker"}
    if not connector in connectors:
        msg = f"\ninvalid connector '{connector}'! Available connectors: {connectors}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return None
    kwargs["connector"] = connector
    # check source
    sourcesPath = os.path.join(sts.settingsPath, "sources")
    sources = [p[:-3] for p in os.listdir(sourcesPath) if p.endswith(".py") and p != "__init__.py"]
    if not any([source.endswith(src) for src in sources]) and (source != "application"):
        msg = f"\ninvalid source '{source}'! Available sources: {sources}"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        return None
    elif source.endswith(".kdbx"):
        kwargs["source"] = helpers.unalias_path(source)
    else:
        kwargs["source"] = source
    return kwargs
