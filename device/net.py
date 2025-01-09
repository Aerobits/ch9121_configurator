from netifaces import ifaddresses, AF_INET
from sys import exit


def get_broadcast_address(interface: str):
    try:
        return ifaddresses(interface)[AF_INET][0]["broadcast"]
    except (ValueError, KeyError):
        print(
            "Automatic broadcast lookup failed. Is the interface specified correctly?"
        )
        exit(1)
