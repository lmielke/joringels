# serve.py

from joringels.src.joringels import Joringel
import joringels.src.settings as sts
import joringels.src.arguments as arguments


def run(*args, **kwargs) -> None:
    j = Joringel(*args, **kwargs)
    j._digest(*args, **kwargs)
    j._update_joringels_appParams(*args, **kwargs)
    j._serve(*args, **kwargs)


def main(*args, **kwargs) -> None:
    return run(*args, **kwargs)


if __name__ == "__main__":
    main(**arguments.mk_args().__dict__)
