import argparse
import subprocess
import platform
import re
import sys

from time import sleep

import psutil
import PySimpleGUI as sg

parser = argparse.ArgumentParser(
    prog="CH9121 Programmer",
    description="Multiple actions may be specified and performed,"
    " in the order specified below.",
)
parser.add_argument(
    "-s",
    "--set",
    default=False,
    action="store_true",
    help="Program device with specified configuration.",
)
parser.add_argument(
    "-g",
    "--get",
    default=False,
    action="store_true",
    help="Download device configuration. Save to file specified by --output-file",
)
parser.add_argument(
    "-r",
    "--reset",
    default=False,
    action="store_true",
    help="Restore device to factory settings",
)
args = parser.parse_args()

if not (args.get or args.reset or args.set):
    parser.print_help()
    sys.exit()


def ping_ip(ip_address):
    """Checking IP - PING"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(
        ["ping", param, "1", ip_address], capture_output=True, text=True, check=False
    )
    # print(result)
    # returncode = 0 gdy IP zajęty, != 0 kiedy wolny
    return result.returncode != 0


def extract_numbered_items(text):
    """extract items"""
    pattern = r"\d+\.\s*(\S+)"
    matches = re.findall(pattern, text)
    return matches


def list_network_interfaces():
    """Get network interfaces"""
    interfaces = list(psutil.net_if_addrs().keys())
    return interfaces


def list_drs():
    """Get DRS list"""
    drs = list(["DRS-1A", "DRS-1F", "DRS-1U", "DRS-1R"])
    return drs


def gui_choice_list(items: list, text: str):
    """Metod to show GUI list"""
    layout = [
        [sg.Text(text)],
        [sg.Listbox(items, size=(30, len(items)), key="ITEMS")],
        [sg.Button("OK"), sg.Button("Anuluj")],
    ]

    window = sg.Window("Wybierz z listy", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Anuluj"):
            # selected_item = None
            # break
            sys.exit()
        if event == "OK" and values["ITEMS"]:
            selected_item = values["ITEMS"][0]
            break

    window.close()
    return selected_item


def show_interface_selection():
    """Network Interface selection"""
    interfaces = list_network_interfaces()
    selected_interface = gui_choice_list(interfaces, "Wybierz kartę sieciową:")
    return selected_interface


def show_drs_selection():
    """DRS selection"""
    selected_drs = gui_choice_list(list_drs(), "Wybierz DRS-a:")
    return selected_drs


def find_ch9121(interface):
    """Searching CH9121"""
    command = ["python", "ch9121.py", "-f", "-i", interface]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if "No devices found" in result.stdout:
        print("\nNie wykryto żadnego urządzenia ch9121!")
        exit(1)

    lista = extract_numbered_items(result.stdout)
    ch9121 = gui_choice_list(lista, "Wybierz urządzenie:")

    return ch9121


def validate_ip_input(ip: str):
    # validate IP
    ipParts = str(ip).split(".")
    isOK = True

    if len(ipParts) == 4:
        for i in ipParts:
            isOK = len(i) >= 1 and len(i) <= 3
            try:
                i = int(i)
                if i == 0:
                    isOK = False
            except ValueError:
                isOK = False

            if isOK is False:
                break
    else:
        isOK = False

    return isOK


def check_IP():
    """Check if IP is not occupied"""
    # Definicja interfejsu graficznego
    ip = None
    layout = [
        [sg.Text("Wprowadź adres IP:")],
        [sg.Input(size=(30, 1), key="IP"), sg.Button("Sprawdź")],
        [sg.Text("", size=(30, 1), key="OUTPUT")],
        [sg.Text("Wybrany adres IP: ")],
        [sg.Input(size=(30, 1), key="IP_CHOICE"), sg.Button("Potwierdź")],
    ]

    window = sg.Window("Sprawdzanie dostępności IP", layout, finalize=True)
    window["IP_CHOICE"].update("192.168.1.15")

    while True:
        window["IP"].update("192.168.1.")
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            sys.exit()
        if event == "Potwierdź":
            if validate_ip_input(values["IP_CHOICE"].strip()):
                break
            else:
                window["OUTPUT"].update("Wprowadź poprawny adres IP")
        if event == "Sprawdź":
            ip = values["IP"].strip()

            if ip and validate_ip_input(ip):
                is_free = ping_ip(ip)
                message = (
                    f"Adres IP {ip} jest wolny"
                    if is_free
                    else f"Adres IP {ip} jest zajęty"
                )
                window["OUTPUT"].update(message)
                message = f"{ip}"
                window["IP_CHOICE"].update(message)
            else:
                window["OUTPUT"].update("Wprowadź poprawny adres IP")

    window.close()
    return values["IP_CHOICE"].strip()


def get_configuration_ch9121(interface, ch9121_mac):
    """Get configuration from CH9121"""

    print("\nGetting configuration...")
    command = [
        "python",
        "ch9121.py",
        "-g",
        "ch9121_get_conf.txt",
        "-i",
        interface,
        "-m",
        ch9121_mac,
    ]
    subprocess.run(command, capture_output=True, text=True, check=True)
    sleep(2)
    print("Done")

    with open("ch9121_get_conf.txt", "r", encoding="utf-8") as f:
        content = f.read()

    print(content)


def prepare_drs_conf(drs_ip, drs_mac, drs_name):
    content = None

    with open("ch9121_conf_template.txt", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("DRS_IP", drs_ip)
    content = content.replace("DRS_MAC", drs_mac)
    content = content.replace("DRS_NAME", drs_name)

    # print(content)

    with open("ch9121_conf_to_set.txt", "w", encoding="utf-8") as f:
        f.write(content)
    sleep(2)


def set_configuration_ch9121(interface, ch9121_mac):
    """Set configuration from CH9121"""

    print("\nSetting configuration...")
    command = [
        "python",
        "ch9121.py",
        "-s",
        "ch9121_conf_to_set.txt",
        "-i",
        interface,
        "-m",
        ch9121_mac,
    ]
    subprocess.run(command, input="y", capture_output=True, text=True, check=True)
    print("Done")


def factory_reset_ch9121(interface, ch9121_mac):
    """Factory reset CH9121"""

    print("Setting factory reset...")
    command = ["python", "ch9121.py", "-r", "-i", interface, "-m", ch9121_mac]
    subprocess.run(command, input="y", capture_output=True, text=True, check=True)
    print("Done")


def compare_files(file1: str, file2: str) -> bool:
    """Compare two txt files"""

    print("\nChecking if the configuration was successfully uploaded...")

    filesOK = None
    with (
        open(file1, "r", encoding="utf-8") as f1,
        open(file2, "r", encoding="utf-8") as f2,
    ):
        filesOK = f1.read() == f2.read()

    if filesOK is False:
        raise RuntimeError(
            "\nNiepowodzenie - konfiguracja pobrana a wysłana nie są zgodne!\n"
        )
    else:
        print("Done")


if __name__ == "__main__":
    if args.set:
        ip = check_IP()
        print("DRS IP: " + ip)
        interface = show_interface_selection()
        ch9121_mac = find_ch9121(interface)
        print("DRS MAC: " + ch9121_mac)
        drs_name = show_drs_selection()
        print("DRS name: " + drs_name)
        prepare_drs_conf(ip, ch9121_mac, drs_name)
        set_configuration_ch9121(interface, ch9121_mac)
        sleep(2)
        get_configuration_ch9121(interface, ch9121_mac)
        compare_files("ch9121_conf_to_set.txt", "ch9121_get_conf.txt")
        sg.popup(
            "\nSET configuration DONE\n",
            title="Info",
            font=("Arial", 14),
            keep_on_top=True,
        )

    if args.get:
        interface = show_interface_selection()
        ch9121_mac = find_ch9121(interface)
        print("DRS MAC: " + ch9121_mac)
        get_configuration_ch9121(interface, ch9121_mac)
        sg.popup(
            "\nGET configuration DONE\n",
            title="Info",
            font=("Arial", 14),
            keep_on_top=True,
        )

    if args.reset:
        interface = show_interface_selection()
        ch9121_mac = find_ch9121(interface)
        print("DRS MAC: " + ch9121_mac)
        factory_reset_ch9121(interface, ch9121_mac)
        sleep(2)
        get_configuration_ch9121(interface, ch9121_mac)
        sg.popup(
            "\nFactory reset DONE\n", title="Info", font=("Arial", 14), keep_on_top=True
        )
