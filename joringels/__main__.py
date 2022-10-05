"""
    Entry poiont for joringels shell calls 
    ###################################################################################
    
    __main__.py imports the action module from joringels.src.actions >> actionModule.py
                and runs it
                action is provided as first positional argument
    example: joringels chkey -n digiserver

    ###################################################################################
    
    for user info ru: 
        python -m joringels info
    above cmd is identical to
        python -m joringels.src.actions.info


"""

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
    return importlib.import_module(f"joringels.src.actions.{action}")


def main(*args, **kwargs):
    """
    to runable from shell these arguments are passed in
    runs action if legidemit and prints outputs
    """
    kwargs = arguments.mk_args().__dict__

    # kwargs are vakidated against enforced contract
    kwargs = contracts.checks(*args, **kwargs)
    return runable(*args, **kwargs).main(*args, **kwargs)


if __name__ == "__main__":
    main()
