import os


def is_shimbboleth_pytesting() -> bool:
    return os.getenv("SHIMBBOLETH_PYTESTING") == "1"
