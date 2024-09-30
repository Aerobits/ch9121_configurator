# CH9121 configurator

Mini python program to set & get CH9121 chip parameters.

## FAQ

CH9121 receives configuration on broadcast address on port 50000 and
sends replies to broadcast address to port 60000.

## Usage

```cmd
$ python ch9121.py --help
usage: CH9121 Programmer [-h] [-s] [-g] [--set] [-r] [-if INPUT_FILE] [-of OUTPUT_FILE] [-i INTERFACE] [-m MAC] [-b BROADCAST]

Multiple actions may be specified and performed, in the order specified below.

options:
  -h, --help            show this help message and exit
  -s, --search          Search for device
  -g, --get             Download device configuration. Save to file specified by --output-file
  --set                 Program device with specified configuration. Specify --input-file
  -r, --reset           Restore device to factory settings
  -if INPUT_FILE, --input-file INPUT_FILE
                        Configuration input file
  -of OUTPUT_FILE, --output-file OUTPUT_FILE
                        Configuration output file. Defaults to config-saved.yaml
  -i INTERFACE, --interface INTERFACE
                        Specify network interface to use
  -m MAC, --mac MAC     Target MAC. If unspecfied, the program will target the only device on network or stop, if there is more than one. Hexadecimal format with no separators
  -b BROADCAST, --broadcast BROADCAST
                        Specify broadcast IP. Can be determined automatically, if --interface is specified.
```

## Config.yaml

The device allows for reprogramming of read-only parameters and does not restore them upon factory reset.
Since all values must be supplied while programming, the config should be downloaded from the device,
modified, and then reprogrammed.

Also see [the example configuration file](example.yaml).
Note: since read-only parameters still need to be supplied and programmed to the device
(and, despite the name, can be overwritten), the user should download the factory configuration
from the device as base and treat the example as reference only.

```yaml
HW config:
  DHCP Enable: false
  Device Gateway IP: 192.168.1.1
  Device IP: 192.168.1.200
  Device IP Mask: 255.255.255.0
  Device MAC: 50547bb50e55 # in hexadecimal format without separators
  Device subtype: 33 # read only
  Device type: 33 # read only
  Hardware version: 2 # read only
  Module name: "CH9121 " # up to 21 characters
  Serial number: 1 # read only
  Serial port negotiation configuration enable: false
  Software version: 6
Default port config:
  Baudrate: 9600 # 300 - 921600 bps
  Clear RX data buffer on connection enable: false
  DNS Enable: false
  Data size: 8 # 5 - 8 bits
  Destination IP: 192.168.1.100
  Destination port: 1000
  Domain name: "" # ignored when DNS not enabled
  Local port number: 2000
  Netmode: 1 # 0 - TCP Server 1 - TCP Client 2 - UDP Server 3 - UDP Client
  PHY Change Handle Enable: true
  Parity: 4 # 0 - odd parity 1 - even parity 2 - mark bit 4 - no parity
  Port Enable: true
  Port subdevice serial number: 1
  RX Packet Max Length: 1024 # up to 1024
  RX Timeout: 0 # max time to wait before sending buffered packets. Units of 10 ms
  Random local port enable: true
  Stop bits: 1 # 0 - 1 stop bit 2 - 1.5 stop bits 2 - 2 stop bits
Auxiliary port config:
  Baudrate: 9600
  Clear RX data buffer on connection enable: false
  DNS Enable: false
  Data size: 8
  Destination IP: 192.168.1.100
  Destination port: 2000
  Domain name: ""
  Local port number: 3000
  Netmode: 2
  PHY Change Handle Enable: true
  Parity: 4
  Port Enable: false
  Port subdevice serial number: 0
  RX Packet Max Length: 1024
  RX Timeout: 0
  Random local port enable: true
  Stop bits: 1
```
