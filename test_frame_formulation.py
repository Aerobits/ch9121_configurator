from device import communication_frame
import unittest


class TestFrameFormulation(unittest.TestCase):
    def test_search_frame(self):
        search_packet = "43 48 39 31 32 31 5F 43 46 47 5F 46 4C 41 47 00 04 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
        search_packet = search_packet.replace(" ", "")
        search_packet = bytes.fromhex(search_packet)

        search_packet_created = communication_frame.search_frame()

        self.assertEqual(search_packet, search_packet_created)

    def test_get_frame_header(self):
        get_packet = """43 48 39 31 32 31 5F 43 46 47 5F 46 4C 41 47 00 02 84 C2 56 98 79 89 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"""
        get_packet = get_packet.replace(" ", "").replace("\n", "")
        get_packet = bytes.fromhex(get_packet)
        module_mac = bytes.fromhex("84 C2 56 98 79 89".replace(" ", ""))
        get_packet_created = communication_frame.get_frame(module_mac=module_mac)
        self.assertEqual(get_packet, get_packet_created)

    def test_get_set_frame_payload(self):
        configuration_request_packet = """
            43 48 39 31 32 31 5F 43 46 47 5F 46 4C 41 47 00 01 84 C2 56 98 79 89 F4 8E 38
            8B FC 9F CC 21 21 01 02 03 43 48 39 31 32 31 20 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 02 03 04 05 06 07 C0 A8 01 14 C0 A8 01 01 FF FF FF 00 00 50 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 FF FF FF FF FF FF FF FF
            00 00 02 01 B8 0B C0 A8 01 64 D0 07 80 25 00 00 08 01 04 01 00 04 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF 01 01 01 00 D0 07 C0 A8 01 0A E8 03 00
            C2 01 00 08 01 04 01 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
            00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"""
        configuration_request_packet = configuration_request_packet.replace(
            " ", ""
        ).replace("\n", "")
        configuration_request_packet = bytes.fromhex(configuration_request_packet)

        command_header, ch9121_mac, pc_mac, data_area_len, data = (
            communication_frame.deserialize_header(configuration_request_packet)
        )

        config = communication_frame.deserialize_config(data)
        data_serialized = communication_frame.serialize_config(config)
        data_deserialized = communication_frame.deserialize_config(data_serialized)

        # In the frame supplied by the manufacturer, some reserved fields are nonzero.
        # Since they are not parsed, frames in binary format cannot be compared, only in config format

        self.assertEqual(config, data_deserialized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
