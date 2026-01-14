
import logging
import time

class Sinocare:

    def __init__(self, address, repository):
        self.logger = logging.getLogger(__name__)
        self.address = address
        self.repository = repository
        self.last_weight = None
        self.repeat_count = 0

    def handler(self, device, advertising):
        address = device.address.lower()
        if address != self.address:
            return False

        for data in advertising.manufacturer_data.values():
            valid = self.verify_checksum(data)
            if valid: break
        else:
            self.logger.warning('Received invalid manufacturer data from scale: %s', address)
            return False

        weight = self.calc_weight(data)

        if self.repeat_count > 5 and weight == 0 and self.last_weight > 0:
            attribute = 'weight.measured_value'
            value = float(self.last_weight)
            timestamp = int(time.time())

            self.logger.info('Attributes of device (%s) changed: %s=%s', address, attribute, value)
            self.repository.append(address, attribute, value, timestamp)

        self.repeat_count = 0 if weight != self.last_weight else self.repeat_count + 1
        self.last_weight = weight

        return True

    def verify_checksum(self, data, offset=6):
        if len(data) < offset + 10:
            return False

        expected = data[offset + 10]
        checksum = 0

        for index in range(offset, offset + 10):
            checksum ^= data[index]
        return checksum == expected

    def calc_weight(self, data, offset=0):
        if len(data) < offset + 10:
            return False

        upper = data[offset + 10] & 0xff
        lower = data[offset +  9] & 0xff

        weight = (upper << 8 | lower) / 100.0
        return weight

