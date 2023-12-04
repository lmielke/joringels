# serve.py
# jo serve -n $DATASAFENAME -con $PROJECTNAME -rt
import os
from joringels.src.joringels_server import JoringelsServer
import joringels.src.settings as sts
import joringels.src.helpers as helpers
import joringels.src.arguments as arguments


def run(*args, host=None, **kwargs) -> None:
    if host is None or os.name == "nt":
        kwargs["host"] = sts.defaultHost
    JoringelsServer(*args, **kwargs).server(*args, **kwargs)


def main(*args, **kwargs) -> None:
    return run(*args, **kwargs)


if __name__ == "__main__":
    main(**arguments.mk_args().__dict__)
