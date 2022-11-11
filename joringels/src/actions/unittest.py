# info.py
import joringels.src.settings as sts
import joringels.test.logunittest as logunittest
import subprocess
import os, sys
import configparser


import colorama as color

color.init()


def main(*args, **kwargs):
    logunittest.main(*args, **kwargs)


if __name__ == "__main__":
    main()
