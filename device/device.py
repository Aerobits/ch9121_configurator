import socket
import time
import threading
from . import protocol
from . import communication_frame
from sys import exit

send_port = 50000
receive_port = 60000

SO_BINDTODEVICE = 25


def send_data(data, broadcast_ip, port):
    socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    socket_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    time.sleep(0.1)
    socket_send.sendto(data, (broadcast_ip, port))


class CH9121:
    def __init__(
        self,
        broadcast_ip,
        interface=None,
        send_port=send_port,
        receive_port=receive_port,
    ):
        self.socket_receive = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.socket_receive.bind(("", receive_port))
        if interface is not None:
            try:
                self.socket_receive.setsockopt(
                    socket.SOL_SOCKET, SO_BINDTODEVICE, str(interface).encode()
                )
            except OSError as error:
                print(
                    "Could not specify interface: ",
                    error,
                    "- Interface specification ignored.",
                )
        self.socket_receive.settimeout(3)
        self.target_ip = broadcast_ip
        self.target_port = send_port
        self.search_max_devices = 5

    def search(self):
        search_packet = communication_frame.search_frame()
        t = threading.Thread(
            target=send_data, args=(search_packet, self.target_ip, self.target_port)
        )
        t.start()
        try:
            response = self.socket_receive.recv(
                protocol.message_size * self.search_max_devices
            )
        except TimeoutError:
            response = None
        responses_count = (
            int(len(response) / protocol.message_size) if response is not None else 0
        )
        device_macs = []
        for i in range(responses_count):
            command_header, ch9121_mac, pc_mac, data_area_len, data = (
                communication_frame.deserialize_header(
                    response[
                        i * protocol.message_size : (i + 1) * protocol.message_size
                    ]
                )
            )
            assert command_header == protocol.Ack.ACK_SEARCH.value
            device_macs.append(ch9121_mac)
        t.join()
        return device_macs

    def get_config(self, module_mac=None):
        get_packet = communication_frame.get_frame(module_mac=module_mac)
        t = threading.Thread(
            target=send_data, args=(get_packet, self.target_ip, self.target_port)
        )
        t.start()
        try:
            response = self.socket_receive.recv(protocol.message_size)
        except TimeoutError:
            print("Timed out waiting for a get response packet. Terminating")
            exit(1)
        command_header, ch9121_mac, pc_mac, data_area_len, data = (
            communication_frame.deserialize_header(response)
        )
        if command_header == protocol.Ack.ACK_GET.value:
            print("Device responded with ACK")
        elif command_header == protocol.NAck.NACK_GET.value:
            print("Device responded with NACK. Terminating.")
            exit(1)
        config = communication_frame.deserialize_config(data)
        t.join()

        return config

    def set_config(self, config, module_mac):
        set_packet = communication_frame.set_frame(config, module_mac=module_mac)
        t = threading.Thread(
            target=send_data, args=(set_packet, self.target_ip, self.target_port)
        )
        t.start()
        try:
            response = self.socket_receive.recv(protocol.message_size)
            command_header, ch9121_mac, pc_mac, data_area_len, data = (
                communication_frame.deserialize_header(response)
            )
            if command_header == protocol.Ack.ACK_SET.value:
                print("Device responded with ACK")
            elif command_header == protocol.NAck.NACK_SET.value:
                print("Device responded with NACK")
                exit(1)
            else:
                print("Return command header unknown")
                exit(1)
        except TimeoutError:
            print("Timed out waiting for response. Terminating")
            exit(1)
        t.join()

    def reset_to_factory_settings(self, module_mac):
        reset_packet = communication_frame.reset_frame(module_mac)
        t = threading.Thread(
            target=send_data, args=(reset_packet, self.target_ip, self.target_port)
        )
        t.start()
        try:
            response = self.socket_receive.recv(protocol.message_size)
            command_header, ch9121_mac, pc_mac, data_area_len, data = (
                communication_frame.deserialize_header(response)
            )
            if command_header == protocol.Ack.ACK_RESET_TO_FACTORY.value:
                print("Device responded with ACK")
            else:
                print("Return command header unknown")
        except TimeoutError:
            print("Timed out waiting for response")
        t.join()
