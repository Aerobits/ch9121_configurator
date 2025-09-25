# CH9121 configurator

Mini python program to set & get CH9121 chip parameters.

## FAQ

CH9121 receives configuration on broadcast address on port 50000 and
sends replies to broadcast address to port 60000.

## Usage of GUI

## Usage GUI

GUI not work on UV (due to Tcl/Tk)
If you want use GUI install ``python3 -m pip install -r gui_requirements.txt``
In VS-Code task you find predefined tasks.
`Ctrl+Shift+P` --> ``Run Task`` --> eg. ``CH9121 Set configuration (with GUI)``

## Usage (without gui)

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

#### Config parameters descriptions

| Parameter 	| Description 	| Accepted values 	|
|---	|---	|---	|
| Device MAC 	| In hexadecimal format, without separators 	| N/A 	|
| Device subtype 	| Read only 	| N/A 	|
| Device type 	| Read only 	| N/A 	|
| Module name 	| Up to 21 characters 	| ASCII strings up to 21 characters 	|
| Serial number 	| Read only 	| N/A 	|
| Baudrate 	| UART Baud	| 300 - 921600 bps 	|
| Data size 	| UART Data size	| 5 - 8 bits 	|
| Domain name 	| Ignored when DNS not enabled 	| N/A 	|
| Netmode 	| Enumeration 	| 0 - TCP Server<br>1 - TCP Client<br>2 - UDP Server<br>3 - UDP Client 	|
| Parity 	| Enumeration 	| 0 - odd parity<br>1 - even parity<br>2 - mark bit<br>4 - no parity 	|
| RX Packet Max Length 	| Max packet / buffer size | up to 1024 	|
| RX Timeout 	| Max time to wait before sending buffered data. Units of 10s of ms. 	| N/A 	|
| Stop bits 	| Enumeration 	| 0 - 1 stop bit<br>2 - 1.5 stop bits<br>2 - 2 stop bits 	|

#### YAML File Example

```yaml
HW config:
  DHCP Enable: false
  Device Gateway IP: 192.168.1.1
  Device IP: 192.168.1.15
  Device IP Mask: 255.255.255.0
  Device MAC: 50547bb50e55 
  Device subtype: 33
  Device type: 33
  Hardware version: 2
  Module name: "CH9121 "
  Serial number: 1
  Serial port negotiation configuration enable: false
  Software version: 6
Default port config:
  Baudrate: 115200
  Clear RX data buffer on connection enable: false
  DNS Enable: false
  Data size: 8
  Destination IP: 192.168.1.100
  Destination port: 1000
  Domain name: ""
  Local port number: 2000
  Netmode: 0
  PHY Change Handle Enable: true
  Parity: 4
  Port Enable: true
  Port subdevice serial number: 1
  RX Packet Max Length: 1024
  RX Timeout: 0
  Random local port enable: true
  Stop bits: 1
Auxiliary port config:
  Baudrate: 9600
  Clear RX data buffer on connection enable: false
  DNS Enable: false
  Data size: 8
  Destination IP: 192.168.1.100
  Destination port: 2000
  Domain name: ""
  Local port number: 3000
  Netmode: 1
  PHY Change Handle Enable: true
  Parity: 4
  Port Enable: false
  Port subdevice serial number: 0
  RX Packet Max Length: 1024
  RX Timeout: 0
  Random local port enable: true
  Stop bits: 1
```

--------------------------------------------------

## IMPORTANT INFO

### WHAT WE NEED TO SET

- Device IP
- Module name
- Default port config - baudrate: 115200
- Default port config - Local port number: 2000
- Default port config - Netmode: 0

### Factory reset

It is possible to restore the device to factory settings.
But in default CH9121 has a set address to **192.168.1.240** and it is **collision in our LAN**. Change it quickly or use VLAN or other separate network.
