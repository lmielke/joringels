# info.py
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import logunittest.actions.info as lut
import subprocess
import os, sys
import configparser


import colorama as color

color.init()


def main(*args, connector=None, **kwargs):
    lut.main(*args, pgName=connector if connector else sts.appName, **kwargs)


if __name__ == "__main__":
    main()
