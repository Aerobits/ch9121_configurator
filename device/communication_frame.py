import struct
from . import protocol
import ipaddress


def search_frame():
    return serialize(
        command=protocol.Commands.SEARCH, module_mac=bytes.fromhex("0" * 12)
    )


def get_frame(module_mac=None):
    return serialize(command=protocol.Commands.GET, module_mac=module_mac)


def set_frame(config, module_mac=None):
    return serialize(
        command=protocol.Commands.SET,
        module_mac=module_mac,
        payload=serialize_config(config),
    )


def reset_frame(module_mac=None):
    return serialize(command=protocol.Commands.RESET_TO_FACTORY, module_mac=module_mac)


def deserialize_header(bytes_buffer):
    deserialize_format = "16sB6s6sB"
    comm_flag, command_header, ch9121_mac, pc_mac, data_area_len = struct.unpack(
        deserialize_format, bytes_buffer[:30]
    )
    data = bytes_buffer[30 : 30 + data_area_len]
    return command_header, ch9121_mac, pc_mac, data_area_len, data


def serialize(
    command: protocol.Commands,
    module_mac=bytes.fromhex(12 * "f"),
    pc_mac=bytes.fromhex(12 * "0"),
    payload=None,
):
    length = len(payload) if payload is not None else 0
    serialize_format = "B6s6sB"
    if payload is None:
        payload = bytes.fromhex(protocol.payload_size * 2 * "0")
    elif len(payload) < protocol.payload_size:
        pad_amount = protocol.payload_size - len(payload)
        payload += bytes.fromhex(2 * pad_amount * "0")
    elif len(payload) > protocol.payload_size:
        raise ValueError("Message data section too long")
    header = struct.pack(serialize_format, command.value, module_mac, pc_mac, length)

    message = protocol.preamble + header + payload
    return message


def deserialize_config(data_bytes):
    """
    struct __attribute__((__packed__)) DEVICEHW_CONFIG
    {
        UCHAR bDevType;                         /* device type, read-only*/
        UCHAR bAuxDevType;                      /* device subtype, read-only*/
        UCHAR bIndex;                           /* device serial number, read-only*/
        UCHAR bDevHardwareVer;                  /* device hardware version number, read-only*/
        UCHAR bDevSoftwareVer;                  /* device software version number, read-only*/
        UCHAR szModulename[21];                 /* user name is the same as CH9121 name*/
        UCHAR bDevMAC[6];                       /* CH9121 network MAC address */
        UCHAR bDevIP[4];                        /* CH9121 IP address */
        UCHAR bDevGWIP[4];                      /* CH9121 gateway IP */
        UCHAR bDevIPMask[4];                    /* CH9121 subnet mask */
        UCHAR bDhcpEnable;                      /* DHCP enable, whether to enable DHCP, 1: enable, 0: not enable*/
        USHORT breserved1;                      /* reserved but not yet enabled*/
        UCHAR breserved2[8];                    /* reserved but not yet enabled*/
        UCHAR breserved3;                       /* reserved but not yet enabled*/
        UCHAR breserved4[8];                    /* reserved but not yet enabled*/
        UCHAR breserved5;                       /* reserved but not yet enabled*/
        UCHAR bComcfgEn;                        /* serial port negotiation configuration flag 1: Enable 0: Disable */
        UCHAR breserved6[8];                    /* reserved but not yet enabled*/
    };
    """
    # deserialize DEVICEHW_CONFIG
    deserialization_format = "BBBBB21s6s4s4s4sBBB8sB8sBB8s"
    device_hw_config = data_bytes[: protocol.device_hw_config_size]
    (
        dev_type,
        aux_dev_type,
        sn,
        hardware_ver,
        software_ver,
        module_name,
        dev_mac,
        dev_ip,
        dev_gateway_ip,
        dev_ip_mask,
        dhcp_enable,
        reserved_1,
        reserved_1a,
        reserved_2,
        reserved_3,
        reserved_4,
        reserved_5,
        b_com_cfg_en,
        reserved_6,
    ) = struct.unpack(deserialization_format, device_hw_config)

    hw_config = {
        "Device type": dev_type,
        "Device subtype": aux_dev_type,
        "Serial number": sn,
        "Hardware version": hardware_ver,
        "Software version": software_ver,
        "Module name": module_name.decode().rstrip("\x00"),
        "Device MAC": dev_mac.hex(),
        "Device IP": str(ipaddress.IPv4Address(dev_ip)),
        "Device Gateway IP": str(ipaddress.IPv4Address(dev_gateway_ip)),
        "Device IP Mask": str(ipaddress.IPv4Address(dev_ip_mask)),
        "DHCP Enable": bool(dhcp_enable),
        "Serial port negotiation configuration enable": bool(b_com_cfg_en),
    }

    # deserialize DEVICEPORT_CONFIG
    # note: ULONG is 4 bytes wide
    deserialization_format = "BBBBH4sHiBBBBiiBBB20s14s"
    device_port_1_config_bytes = data_bytes[
        protocol.device_hw_config_size : protocol.device_hw_config_size
        + protocol.device_port_config_size
    ]
    device_port_2_config_bytes = data_bytes[
        protocol.device_hw_config_size
        + protocol.device_port_config_size : protocol.device_hw_config_size
        + 2 * protocol.device_port_config_size
    ]
    """
    struct __attribute__((__packed__)) DEVICEPORT_CONFIG
    {
        UCHAR bIndex;                           /* sub-device serial number, read-only */
        UCHAR bPortEn;                          /* port enable flag 1: Enable; 0: Disable*/
        UCHAR bNetMode;                         /* network working mode: 0: TCP SERVER; 1: TCP CLENT; 2: UDP SERVER 3: UDP CLIENT; */
        UCHAR bRandSportFlag;                   /* random local port number in TCP client mode, 1: random 0: not random*/
        USHORT wNetPort;                        /* local port number*/  
        UCHAR bDesIP[4];                        /* destination IP address */
        //10
        USHORT wDesPort;                        /* destination port number*/
        ULONG dBaudRate;                        /* serial port baud rate: 300---921600bps */
        UCHAR bDataSize;                        /* serial port data bits: 5---8 bits*/  
        UCHAR bStopBits;                        /* serial port stop bit: 0 means 1 stop bit; 1 means 1.5 stop bits; 2 means 2 stop bits*/  
        UCHAR bParity;                          /* serial port parity bit: 4 means no parity, 0 means odd parity; 1 means even parity; 2 means mark bit (MARK, set to 1); 3 means space bit (SPACE, clear to 0); */    
        UCHAR bPHYChangeHandle;                 /* PHY disconnected, Socket action, 1: close Socket 0: no action*/
        // 20
        ULONG dRxPktlength;                     /* serial port RX data packet length, maximum 1024 */
        ULONG dRxPktTimeout;                    /* maximum waiting time for serial port RX data package forwarding, unit: 10ms, 0 means turning off the timeout function*/
        UCHAR bResv;                            /* reserved not enabled*/  
        UCHAR bResetCtrl;                       /* serial port reset operation: 0 means do not clear the serial port data buffer; 1 means clear the serial port data buffer when connected */  
        // 30
        UCHAR bDNSFlag;                         /* domain name function enable flag, 1: enable 0: disable */
        UCHAR szDomainname[20];                 /* In TCP client mode, destination address, domain name*/
        UCHAR breserved[14];                    /* reserved */
        // 65
    };
    """
    (
        subdev_serial,
        port_en,
        netmode,
        random_local_port,
        local_port_number,
        dest_ip,
        dest_port,
        baud,
        data_size,
        stop_bits,
        parity,
        phy_handle,
        rx_packet_length,
        rx_timeout,
        reserved_1,
        reset_ctl,
        dns_flag,
        domain_name,
        reserved,
    ) = struct.unpack(deserialization_format, device_port_1_config_bytes)
    port_1_cfg = {
        "Port subdevice serial number": subdev_serial,
        "Port Enable": bool(port_en),
        "Netmode": netmode,
        "Random local port enable": bool(random_local_port),
        "Local port number": local_port_number,
        "Destination IP": str(ipaddress.IPv4Address(dest_ip)),
        "Destination port": dest_port,
        "Baudrate": baud,
        "Data size": data_size,
        "Stop bits": stop_bits,
        "Parity": parity,
        "PHY Change Handle Enable": bool(phy_handle),
        "RX Packet Max Length": rx_packet_length,
        "RX Timeout": rx_timeout,
        "Clear RX data buffer on connection enable": bool(reset_ctl),
        "DNS Enable": bool(dns_flag),
        "Domain name": domain_name.decode().rstrip("\x00"),
    }
    (
        subdev_serial,
        port_en,
        netmode,
        random_local_port,
        local_port_number,
        dest_ip,
        dest_port,
        baud,
        data_size,
        stop_bits,
        parity,
        phy_handle,
        rx_packet_length,
        rx_timeout,
        reserved_1,
        reset_ctl,
        dns_flag,
        domain_name,
        reserved,
    ) = struct.unpack(deserialization_format, device_port_2_config_bytes)

    port_2_cfg = {
        "Port subdevice serial number": subdev_serial,
        "Port Enable": bool(port_en),
        "Netmode": netmode,
        "Random local port enable": bool(random_local_port),
        "Local port number": local_port_number,
        "Destination IP": str(ipaddress.IPv4Address(dest_ip)),
        "Destination port": dest_port,
        "Baudrate": baud,
        "Data size": data_size,
        "Stop bits": stop_bits,
        "Parity": parity,
        "PHY Change Handle Enable": bool(phy_handle),
        "RX Packet Max Length": rx_packet_length,
        "RX Timeout": rx_timeout,
        "Clear RX data buffer on connection enable": bool(reset_ctl),
        "DNS Enable": bool(dns_flag),
        "Domain name": domain_name.decode().rstrip("\x00"),
    }
    config = {
        "HW config": hw_config,
        "Default port config": port_2_cfg,
        "Auxiliary port config": port_1_cfg,
    }
    return config


def serialize_config(config):
    # serialize DEVICEHW_CONFIG

    # read_only parameters
    hw_config = config["HW config"]
    dev_type = hw_config["Device type"]
    aux_dev_type = hw_config["Device subtype"]
    sn = hw_config["Serial number"]
    hardware_ver = hw_config["Hardware version"]
    software_ver = hw_config["Software version"]
    module_name = hw_config["Module name"].encode()
    dev_mac = int(hw_config["Device MAC"], 16).to_bytes(6, byteorder="big")
    dev_ip = int(ipaddress.IPv4Address(hw_config["Device IP"])).to_bytes(
        4, byteorder="big"
    )
    dev_gateway_ip = int(
        ipaddress.IPv4Address(hw_config["Device Gateway IP"])
    ).to_bytes(4, byteorder="big")
    dev_ip_mask = int(ipaddress.IPv4Address(hw_config["Device IP Mask"])).to_bytes(
        4, byteorder="big"
    )
    dhcp_enable = hw_config["DHCP Enable"]
    b_com_cfg_en = hw_config["Serial port negotiation configuration enable"]

    reserved_1, reserved_1a, reserved_3, reserved_5 = [0 for _ in range(4)]
    reserved_2, reserved_4, reserved_6 = [bytes(0) for _ in range(3)]

    serialization_format = "BBBBB21s6s4s4s4sBBB8sB8sBB8s"
    device_hw_config_data = struct.pack(
        serialization_format,
        dev_type,
        aux_dev_type,
        sn,
        hardware_ver,
        software_ver,
        module_name,
        dev_mac,
        dev_ip,
        dev_gateway_ip,
        dev_ip_mask,
        dhcp_enable,
        reserved_1,
        reserved_1a,
        reserved_2,
        reserved_3,
        reserved_4,
        reserved_5,
        b_com_cfg_en,
        reserved_6,
    )

    # serialize DEVICEPORT_CONFIG
    # note: ULONG is 4 bytes wide
    serialization_format = "BBBBH4sHiBBBBiiBBB20s14s"
    port_1_config = config["Auxiliary port config"]
    subdev_serial = port_1_config["Port subdevice serial number"]
    port_en = port_1_config["Port Enable"]
    netmode = port_1_config["Netmode"]
    random_local_port = port_1_config["Random local port enable"]
    local_port_number = port_1_config["Local port number"]
    dest_ip = int(ipaddress.IPv4Address(port_1_config["Destination IP"])).to_bytes(
        4, byteorder="big"
    )
    dest_port = port_1_config["Destination port"]
    baud = port_1_config["Baudrate"]
    data_size = port_1_config["Data size"]
    stop_bits = port_1_config["Stop bits"]
    parity = port_1_config["Parity"]
    phy_handle = port_1_config["PHY Change Handle Enable"]
    rx_packet_length = port_1_config["RX Packet Max Length"]
    rx_timeout = port_1_config["RX Timeout"]
    reset_ctl = port_1_config["Clear RX data buffer on connection enable"]
    dns_flag = port_1_config["DNS Enable"]
    domain_name = port_1_config["Domain name"].encode()
    reserved = bytes(0)

    port_1_config_data = struct.pack(
        serialization_format,
        subdev_serial,
        port_en,
        netmode,
        random_local_port,
        local_port_number,
        dest_ip,
        dest_port,
        baud,
        data_size,
        stop_bits,
        parity,
        phy_handle,
        rx_packet_length,
        rx_timeout,
        reserved_1,
        reset_ctl,
        dns_flag,
        domain_name,
        reserved,
    )

    port_2_config = config["Default port config"]
    subdev_serial = port_2_config["Port subdevice serial number"]
    port_en = port_2_config["Port Enable"]
    netmode = port_2_config["Netmode"]
    random_local_port = port_2_config["Random local port enable"]
    local_port_number = port_2_config["Local port number"]
    dest_ip = int(ipaddress.IPv4Address(port_2_config["Destination IP"])).to_bytes(
        4, byteorder="big"
    )
    dest_port = port_2_config["Destination port"]
    baud = port_2_config["Baudrate"]
    data_size = port_2_config["Data size"]
    stop_bits = port_2_config["Stop bits"]
    parity = port_2_config["Parity"]
    phy_handle = port_2_config["PHY Change Handle Enable"]
    rx_packet_length = port_2_config["RX Packet Max Length"]
    rx_timeout = port_2_config["RX Timeout"]
    reset_ctl = port_2_config["Clear RX data buffer on connection enable"]
    dns_flag = port_2_config["DNS Enable"]
    domain_name = port_2_config["Domain name"].encode()
    reserved = bytes(0)

    port_2_config_data = struct.pack(
        serialization_format,
        subdev_serial,
        port_en,
        netmode,
        random_local_port,
        local_port_number,
        dest_ip,
        dest_port,
        baud,
        data_size,
        stop_bits,
        parity,
        phy_handle,
        rx_packet_length,
        rx_timeout,
        reserved_1,
        reset_ctl,
        dns_flag,
        domain_name,
        reserved,
    )

    message_payload = device_hw_config_data + port_1_config_data + port_2_config_data

    return message_payload
