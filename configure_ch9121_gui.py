import sys
import os
import platform
import questionary
import argparse
import subprocess
import re
import psutil

from time import sleep

# ----------------------------------------------------------------------------- #

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

# ----------------------------------------------------------------------------- #


def clear_screen():
    """Czyści ekran w CMD"""
    os.system("cls" if platform.system().lower() == "windows" else "clear")


def validate_ip_input(ip: str) -> bool:
    """Sprawdza poprawność IP (bez 0, zakres 1–255, brak pustych oktetów)"""
    parts = ip.strip().split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num <= 0 or num > 255:
            return False
    return True


def ping_ip(ip_address: str) -> bool:
    """Sprawdza zajętość IP (return True jeśli wolny, False jeśli zajęty)"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(
        ["ping", param, "1", ip_address],
        capture_output=True,
        text=True,
        check=False,
    )
    # returncode == 0 → IP odpowiada → zajęty
    return result.returncode != 0


def terminal_choice_list(items: list, text: str):
    """Function to show a list in terminal and let user choose with arrows"""
    if not items:
        print("Brak elementów do wyboru.")
        sys.exit(1)

    selected_item = questionary.select(text, choices=items, qmark="▶").ask()

    if selected_item is None:
        sys.exit()

    return selected_item


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


def show_interface_selection():
    """Network Interface selection"""
    interfaces = list_network_interfaces()
    selected_interface = terminal_choice_list(interfaces, "Wybierz kartę sieciową:")
    return selected_interface


def show_drs_selection():
    """DRS selection"""
    selected_drs = terminal_choice_list(list_drs(), "Wybierz DRS-a:")
    return selected_drs


def find_ch9121(interface):
    """Searching CH9121"""
    command = ["python", "ch9121.py", "-f", "-i", interface]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if "No devices found" in result.stdout:
        print("\nNie wykryto żadnego urządzenia ch9121!")
        exit(1)

    lista = extract_numbered_items(result.stdout)
    ch9121 = terminal_choice_list(lista, "Wybierz urządzenie [MAC]:")

    return ch9121


def check_IP_cmd():
    base_ip = "192.168.1."
    chosen_ip = None
    ip_validate_info = ""
    ip_is_free = False
    ip_input = ""

    print("=== Sprawdzanie zajętości adresu IP ===")
    print("")
    ip_input = input(f"Wpisz adres IP: {base_ip}").strip()
    ip = base_ip + ip_input if ip_input else ""
    if not validate_ip_input(ip):
        ip_validate_info = f"⚠️ Niepoprawny format adresu IP: {ip}"
        ip_is_free = None
    else:
        # Sprawdzamy czy IP jest wolny
        ip_is_free = ping_ip(ip)
        status = "✅ wolny" if ip_is_free else "❌ zajęty"
        ip_validate_info = f"Adres IP {ip} jest {status}"

    while True:
        clear_screen()
        print("=== Sprawdzanie zajętości adresu IP ===")
        print(ip_validate_info)
        if ip_is_free is not None:
            ip_input = (
                input(
                    f"Zatwierdź {ip} [y/yes] lub Wpisz nowy adres IP: {base_ip}[1-255] "
                )
                .strip()
                .lower()
            )

            if ip_input in ("y", "yes"):
                if not ip_is_free:
                    # dodatkowe potwierdzenie jeśli IP zajęty
                    override = (
                        input(
                            "Adres IP jest już zajęty, czy na pewno chcesz użyć tego adresu? [y/n]: "
                        )
                        .strip()
                        .lower()
                    )
                    if override not in ("y", "yes"):
                        continue
                chosen_ip = ip
                break
        else:
            ip_input = input(f"Wpisz adres IP: {base_ip}").strip()

        ip = base_ip + ip_input if ip_input else ""

        if not validate_ip_input(ip):
            ip_validate_info = f"⚠️ Niepoprawny format adresu IP: {ip}"
            ip_is_free = None
        else:
            # Sprawdzamy czy IP jest wolny
            ip_is_free = ping_ip(ip)
            status = "✅ wolny" if ip_is_free else "❌ zajęty"
            ip_validate_info = f"Adres IP {ip} jest {status}"

    clear_screen()
    print("=== Sprawdzanie zajętości adresu IP ===")
    print(f"✔️  Wybrany adres IP: {chosen_ip}")
    return chosen_ip


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

    print("\n" + content)


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
    clear_screen()
    if args.set:
        ip = check_IP_cmd()
        interface = show_interface_selection()
        ch9121_mac = find_ch9121(interface)
        drs_name = show_drs_selection()

        print("")
        print("DRS IP: " + ip)
        print("DRS MAC: " + ch9121_mac)
        print("DRS name: " + drs_name)
        prepare_drs_conf(ip, ch9121_mac, drs_name)
        set_configuration_ch9121(interface, ch9121_mac)
        sleep(2)
        get_configuration_ch9121(interface, ch9121_mac)
        compare_files("ch9121_conf_to_set.txt", "ch9121_get_conf.txt")
        print("\nSET configuration DONE\n")

    if args.get:
        interface = show_interface_selection()
        ch9121_mac = find_ch9121(interface)
        print("\nDRS MAC: " + ch9121_mac)
        get_configuration_ch9121(interface, ch9121_mac)
        print("\nGET configuration DONE\n")

    # if args.reset:
    #     # warning - after factory reset DRS has 192.168.1.200 IP
    #     #  and it is collision with our network!
    #     interface = show_interface_selection()
    #     ch9121_mac = find_ch9121(interface)
    #     print("\nDRS MAC: " + ch9121_mac)
    #     factory_reset_ch9121(interface, ch9121_mac)
    #     sleep(2)
    #     get_configuration_ch9121(interface, ch9121_mac)
    #     print("\nFactory reset DONE configuration DONE\n")
