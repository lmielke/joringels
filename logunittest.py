"""
    logunittest.py
    entry point for unittest with logging
    imports log_unittest module and runs it

    Description:
                The log_unittest module assumes a certain package folder structure,
                where the top project folder contains a package folder which are
                both named identically. The lower package folder then contains
                a test directory in which the logs directory lives.
"""
import os, re, sys, importlib
sys.path.append(os.path.expanduser(r"~/python_venvs/utils/log_unittest"))
log_unittest = importlib.import_module('log_unittest')

def stats(*args, **kwargs):
    pgPath=os.path.dirname(__file__)
    print(f"{pgPath = }")
    return log_unittest.Coverage(*args, pgPath=pgPath)()


def main(*args, **kwargs):
    log_unittest.main(pgPath=os.path.dirname(__file__))



if __name__ == "__main__":
    main()
