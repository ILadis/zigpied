
import types
import logging

class Observer:

    def __init__(self, repository):
        self.logger = logging.getLogger(__name__)
        self.repository = repository

    def observe(self, controller):
        listener = types.SimpleNamespace()
        listener.device_initialized = self.add_device

        controller.add_listener(listener)

        for device in controller.devices.values():
            self.add_device(device)

    def attribute_changed(self, device, attributes, value):
        address = str(device.ieee)
        timestamp = int(device.last_seen)
        attribute = '.'.join(attributes)

        self.logger.info('Attributes of device (%s) changed: %s=%s', address, attribute, value)

        if isinstance(value, (int, float)):
            self.repository.append(address, attribute, value, timestamp)
        else:
            self.logger.warn('Not appending to repository because attribute value is not numerical')

    def add_device(self, device):
        parse_packet = device._parse_packet_command
        handle_command = self.handle_command
        logger = self.logger

        def parse_command(self, packet, endpoint, cluster):
            command = parse_packet(packet, endpoint, cluster)
            try:
                handle_command(device, endpoint, cluster, command)
            except Exception as exception:
                logger.error(exception, exc_info=True)
            return command

        self.logger.info('Device (%s) is being observed', str(device.ieee))

        device._parse_packet_command = types.MethodType(parse_command, device)

    def handle_command(self, device, endpoint, cluster, command):
        if cluster is None:
            return False
        if not hasattr(command, 'attribute_reports'):
            return False

        for report in command.attribute_reports:
            attrid = report.attrid
            value = report.value.value

            attrdev = cluster.ep_attribute
            attrdef = cluster.find_attribute(attrid).name

            self.attribute_changed(device, [attrdev, attrdef], value)

        return True
