# contracts.py
import joringels.src.settings as sts
import colorama as color

color.init()


def checks(*args, **kwargs):
    error_upload_all(*args, **kwargs)
    kwargs = warn_deletion(*args, **kwargs)
    kwargs['source'] = sts.unalias_path(kwargs['source'])
    return kwargs


def warn_deletion(*args, retain, **kwargs):
    if kwargs["action"] == "serve":
        if retain == False:
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
    if action != 'fetch' and host is not None:
        msg = f"Your -ip, host contains {host}. It must be empty to use load_all!"
        print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        exit()
