import colorama as color

color.init()
import importlib

import joringels.src.settings as sts
import joringels.src.arguments as arguments
import joringels.src.contracts as contracts


def runable(*args, action, **kwargs):
    """
    imports action as a package and executes it
    returns the runable result
    """
    return importlib.import_module(f"{sts.actionImport}.{action}")


def main(*args, **kwargs):
    """
    to runable from shell these arguments are passed in
    runs action if legidemit and prints outputs
    """
    kwargs = arguments.mk_args().__dict__
    kwargs = contracts.checks(*args, **kwargs)
    return runable(*args, **kwargs).main(*args, **kwargs)


if __name__ == "__main__":
    main()
