import argparse

from device import device
from device import store_config
from device import net

# needed by pyinstaller
from sys import exit

parser = argparse.ArgumentParser(
    prog="CH9121 Programmer",
    description="Multiple actions may be specified and performed,"
    " in the order specified below.",
)
parser.add_argument(
    "-f", "--find", default=False, action="store_true", help="Search for device"
)
parser.add_argument(
    "-g",
    "--get",
    default=None,
    help="Download device configuration. Follow this argument by a filename to save the configuration to",
    metavar="Configuration output filename",
)
parser.add_argument(
    "-s",
    "--set",
    default=None,
    help="Program device with specified configuration. "
    "Follow this argument by a filename to source the configuration from",
    metavar="Configuration input filename",
)
parser.add_argument(
    "-r",
    "--reset",
    default=False,
    action="store_true",
    help="Restore device to factory settings",
)
parser.add_argument(
    "-i",
    "--interface",
    default="enxc84d4425916c",
    help="Specify network interface to use",
)
parser.add_argument(
    "-m",
    "--mac",
    default=None,
    help="Target MAC. If unspecfied, "
    "the program will target the only device on network or stop, if there "
    "is more than one. Hexadecimal format with no separators",
)
parser.add_argument(
    "-b",
    "--broadcast",
    default=None,
    help="Specify broadcast IP. "
    "Can be determined automatically, if --interface is specified.",
)
args = parser.parse_args()

if not (args.find or args.get or args.reset or args.set):
    parser.print_help()
    exit(1)

broadcast = (
    args.broadcast
    if args.broadcast is not None
    else net.get_broadcast_address(args.interface)
)
module = device.CH9121(broadcast_ip=broadcast, interface=args.interface)

target_mac = (
    int(args.mac, 16).to_bytes(6, byteorder="big") if args.mac is not None else None
)

if args.find:
    print("Searching")
    module_macs = module.search()

    if module_macs:
        print(
            f"Found {len(module_macs)} device" + "s" * bool(len(module_macs) > 1) + ":"
        )
        for i in range(len(module_macs)):
            print(f"{i + 1}. {module_macs[i].hex()}")

    else:
        print("No devices found")

    if len(module_macs) == 1 and args.mac is None:
        target_mac = module_macs[0]

if args.get:
    if target_mac is None:
        print("No target MAC specified and no available devices found.")
        exit(1)
    print(f"Asking {target_mac.hex()} for its configuration")
    config = module.get_config(module_mac=target_mac)
    store_config.config_save(config, args.get)

if args.set:
    if target_mac is None:
        print("No target MAC specified and no available devices found.")
        exit(1)

    answer = ""
    while answer not in ["y", "n"]:
        answer = input(
            f"Programming the configuration from {args.set} to the device. Ok? [y/n] "
        )

    if answer == "n":
        exit(1)

    print(f"Sending configuration specified in {args.set} to {target_mac.hex()}")
    config = store_config.config_load(args.set)
    config["Device MAC"] = target_mac
    module.set_config(config, module_mac=target_mac)

if args.reset:
    if target_mac is None:
        print("No target MAC specified and no available devices found.")
        exit(1)

    answer = ""
    while answer not in ["y", "n"]:
        answer = input(
            f"Reseting the {target_mac.hex()} to factory settings. Ok? [y/n] "
        )

    if answer == "n":
        exit(1)

    print(f"Asking {target_mac.hex()} to revert to factory settings.")
    module.reset_to_factory_settings(module_mac=target_mac)
