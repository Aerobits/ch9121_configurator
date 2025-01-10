from enum import Enum

message_size = 285
header_size = 30
device_hw_config_size = 74
device_port_config_size = 65
payload_size = message_size - header_size
preamble = bytes.fromhex(
    "43 48 39 31 32 31 5F 43 46 47 5F 46 4C 41 47 00".replace(" ", "")
)


class Commands(Enum):
    SET = 0x01
    GET = 0x02
    RESET_TO_FACTORY = 0x03
    SEARCH = 0x04


class Ack(Enum):
    ACK_SET = 0x81
    ACK_GET = 0x82
    ACK_RESET_TO_FACTORY = 0x83
    ACK_SEARCH = 0x84


class NAck(Enum):
    NACK_SEARCH = 0xC0
    NACK_SET = 0xC1
    NACK_GET = 0xC2
