"""
    Entry poiont for joringels shell calls 
    ###################################################################################
    
    __main__.py imports the action module from joringels.src.actions >> actionModule.py
                and runs it
                action is provided as first positional argument
    example: joringels chkey -n safe_one

    ###################################################################################
    
    for user info run: 
        python -m joringels info
    above cmd is identical to
        python -m joringels.src.actions.info


"""
import os, sys

import colorama as color

color.init()
import importlib

import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.arguments as arguments
import joringels.src.contracts as contracts
import subprocess


def runable(*args, action, **kwargs):
    """
    imports action as a package and executes it
    returns the runable result
    """
    return importlib.import_module(f"joringels.src.actions.{action}")


def run_tests(*args, runTests=None, **kwargs):
    if runTests:
        # runs unittest before serving, NOTE: tries to serve even if test has errors!
        subprocess.call(["pipenv", "run", "python", "-m", "logunittest", "ut"])


def main(*args, **kwargs):
    """
    to runable from shell these arguments are passed in
    runs action if legidemit and prints outputs
    """
    kwargs = arguments.mk_args().__dict__
    # kwargs are vakidated against enforced contract
    kwargs = contracts.checks(*args, **kwargs)
    run_tests(*args, **kwargs)
    return runable(*args, **kwargs).main(*args, **kwargs)


if __name__ == "__main__":
    main()
