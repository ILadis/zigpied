
import zigpied

import unittest
import json

from utils import fetch

class MetricsApiTest(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.server = zigpied.Server()
        self.repository = zigpied.Repository(':memory:')

        from zigpied.handlers import query_metrics
        self.server.register('GET', '/metrics', query_metrics, self.repository)

        await self.server.start('localhost', 8080)

    async def asyncTearDown(self):
        await self.server.stop()

    async def test_querying_one_metric(self):
        # arrange
        self.repository.append(
            address='01:02:03:04:05:06:07:08',
            metric='temperature.measured_value',
            value=2042.0,
            timestamp=1763464983)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(1, len(metrics))
        self.assertEqual('01:02:03:04:05:06:07:08', metrics[0]['address'])
        self.assertEqual('temperature.measured_value', metrics[0]['metric'])
        self.assertEqual('2025-11-18T12:23:03', metrics[0]['timestamp'])
        self.assertEqual(2042.0, metrics[0]['value'])

    async def test_querying_specific_metric(self):
        # arrange
        self.repository.append(
            address='01:02:03:04:05:06:07:08',
            metric='temperature.measured_value',
            value=2042.0,
            timestamp=1763464983)

        self.repository.append(
            address='01:02:03:04:05:06:07:08',
            metric='pressure.measured_value',
            value=964,
            timestamp=1763464983)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics?address=01:02:03:04:05:06:07:08'
                + '&metric=pressure.measured_value'
                + '&after=2025-11-18T12:23:00'
                + '&before=2025-11-18T12:24:00')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(1, len(metrics))
        self.assertEqual('01:02:03:04:05:06:07:08', metrics[0]['address'])
        self.assertEqual('pressure.measured_value', metrics[0]['metric'])
        self.assertEqual('2025-11-18T12:23:03', metrics[0]['timestamp'])
        self.assertEqual(964, metrics[0]['value'])

    async def test_querying_non_existent_metric(self):
        # arrange
        self.repository.append(
            address='01:02:03:04:05:06:07:08',
            metric='temperature.measured_value',
            value=2042.0,
            timestamp=1763464983)

        queries = [
            'address=01:02:03:04:05:06:07:09',
            'metric=pressure.measured_value',
            'before=2025-11-18T12:21:00',
            'after=2025-11-18T12:25:00']

        for query in queries:
            # act
            api = await fetch('GET', 'http://localhost:8080/metrics?' + query)
            metrics = json.loads(api.read() or '[ ]')

            # assert
            self.assertEqual(200, api.status)
            self.assertEqual(0, len(metrics))

    async def test_querying_with_invalid_filters(self):
        # arrange
        self.repository.append(
            address='01:02:03:04:05:06:07:08',
            metric='temperature.measured_value',
            value=2042.0,
            timestamp=1763464983)

        queries = [
            'before=1763464983',
            'before=2025-11-18',
            'after=12:25:00',
            'after=1763464983']

        for query in queries:
            # act
            api = await fetch('GET', 'http://localhost:8080/metrics?' + query)

            # assert
            self.assertEqual(400, api.status)

    async def test_querying_all_metrics(self):
        # arrange
        timestamp = 1763464983
        values = [2042.0, 2127.0, 2291.0]

        for index, value in enumerate(values):
            self.repository.append(
                address='01:02:03:04:05:06:07:08',
                metric='temperature.measured_value',
                value=value,
                timestamp=timestamp + index * 90)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(3, len(metrics))
        self.assertEqual(2042.0, metrics[2]['value'])
        self.assertEqual(2127.0, metrics[1]['value'])
        self.assertEqual(2291.0, metrics[0]['value'])
        self.assertEqual('2025-11-18T12:23:03', metrics[2]['timestamp'])
        self.assertEqual('2025-11-18T12:24:33', metrics[1]['timestamp'])
        self.assertEqual('2025-11-18T12:26:03', metrics[0]['timestamp'])

    async def test_querying_all_metrics_after_datetime(self):
        # arrange
        timestamp = 1763464800

        for index in range(0, 3):
            self.repository.append(
                address='01:02:03:04:05:06:07:08',
                metric='temperature.measured_value',
                value=2042.0,
                timestamp=timestamp + index * 60)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics?after=2025-11-18T12:21:00')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(2, len(metrics))
        self.assertEqual('2025-11-18T12:21:00', metrics[1]['timestamp'])
        self.assertEqual('2025-11-18T12:22:00', metrics[0]['timestamp'])

    async def test_querying_all_metrics_between_datetime(self):
        # arrange
        timestamp = 1763464800

        for index in range(0, 5):
            self.repository.append(
                address='01:02:03:04:05:06:07:08',
                metric='temperature.measured_value',
                value=2042.0,
                timestamp=timestamp + index * 60)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics?after=2025-11-18T12:21:00&before=2025-11-18T12:23:00')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(3, len(metrics))
        self.assertEqual('2025-11-18T12:21:00', metrics[2]['timestamp'])
        self.assertEqual('2025-11-18T12:22:00', metrics[1]['timestamp'])
        self.assertEqual('2025-11-18T12:23:00', metrics[0]['timestamp'])

    async def test_querying_all_metrics_of_address(self):
        # arrange
        values = [2042.0, 2127.0, 2291.0, 1881.0, 1640.0]

        for index, value in enumerate(values):
            self.repository.append(
                address='ff:ff:ff:ff:ff:ff:ff:%0.2x' % index,
                metric='temperature.measured_value',
                value=value,
                timestamp=1763464983)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics?address=ff:ff:ff:ff:ff:ff:ff:03')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(1, len(metrics))
        self.assertEqual(1881.0, metrics[0]['value'])

    async def test_querying_all_metrics_of_type(self):
        # arrange
        values = [(0, 964, 2042.0), (1, 966, 2127.0), (2, 959, 2291.0)]

        for index, pressure, temperature in values:
            self.repository.append(
                address='01:02:03:04:05:06:07:08',
                metric='pressure.measured_value',
                value=pressure,
                timestamp=1763464983 + index)
            self.repository.append(
                address='01:02:03:04:05:06:07:08',
                metric='temperature.measured_value',
                value=temperature,
                timestamp=1763464983 + index)

        # act
        api = await fetch('GET', 'http://localhost:8080/metrics?metric=temperature.measured_value')
        metrics = json.loads(api.read() or '[ ]')

        # assert
        self.assertEqual(200, api.status)
        self.assertEqual(3, len(metrics))
        self.assertEqual(2042.0, metrics[2]['value'])
        self.assertEqual(2127.0, metrics[1]['value'])
        self.assertEqual(2291.0, metrics[0]['value'])
        self.assertEqual('temperature.measured_value', metrics[2]['metric'])
        self.assertEqual('temperature.measured_value', metrics[1]['metric'])
        self.assertEqual('temperature.measured_value', metrics[0]['metric'])

if __name__ == '__main__':
    unittest.main()
