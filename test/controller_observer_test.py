
import zigpied
import zigpy.types as types

import unittest
import json

from utils import noop_controller, add_device

class ControllerObserverTest(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.repository = zigpied.Repository(':memory:')

        self.controller = noop_controller({
            'database_path': ':memory:',
            'device': { 'path': '/dev/ttyUSB0' },
        })

        endpoint, self.address = add_device(self.controller, '01:02:03:04:05:06:07:08', 'ABCD')
        endpoint.add_input_cluster(0x0402) # temperature measurement

        observer = zigpied.Observer(self.repository)
        observer.observe(self.controller)

        await self.controller.initialize(auto_form=False)

    async def asyncTearDown(self):
        await self.controller.shutdown()

    async def test_observing_measured_value_packet(self):
        # arrange
        data = b'\x10\x00\x0A\x00\x00\x29\xBE\x0A'
        #          ^ frame control (global command, direction: server to client)
        #              ^ sequence number
        #                  ^ command id (10 = attribution report)
        #                      ^ attribute id (0 = measured value)
        #                              ^ attr value (data type + value)

        packet = types.ZigbeePacket(
            src=self.address, src_ep=0x1,
            dst=self.address, dst_ep=0x1,
            tsn=self.controller.get_sequence(),
            profile_id=260,
            cluster_id=0x0402,
            data=types.SerializableBytes(data))

        # act
        self.controller.packet_received(packet)
        log = self.repository.query().fetchone()

        # assert
        self.assertEqual('01:02:03:04:05:06:07:08', str(log.address))
        self.assertEqual('temperature.measured_value', str(log.metric))
        self.assertEqual(2750, int(log.value))


if __name__ == '__main__':
    unittest.main()
