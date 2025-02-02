from decimal import Decimal

import json
import unittest

from dsmr_parser import telegram_specifications, obis_references
from dsmr_parser.objects import MbusDevice


class MbusDeviceTest(unittest.TestCase):

    def setUp(self):
        v5_objects = telegram_specifications.V5['objects']

        device_type_parser = [
            object["value_parser"]
            for object in v5_objects
            if object["obis_reference"] == obis_references.DEVICE_TYPE
        ][0]
        device_type = device_type_parser.parse('0-2:24.1.0(003)\r\n')

        equipment_parser = [
            object["value_parser"]
            for object in v5_objects
            if object["obis_reference"] == obis_references.EQUIPMENT_IDENTIFIER_GAS
        ][0]
        equipment = equipment_parser.parse('0-2:96.1.0(4730303339303031393336393930363139)\r\n')

        gas_reading_parser = [
            object["value_parser"]
            for object in v5_objects
            if object["obis_reference"] == obis_references.HOURLY_GAS_METER_READING
        ][0]
        gas_reading = gas_reading_parser.parse('0-2:24.2.1(200426223001S)(00246.138*m3)\r\n')

        mbus_device = MbusDevice(channel_id=1)
        mbus_device.add(obis_references.DEVICE_TYPE, device_type, "DEVICE_TYPE")
        mbus_device.add(obis_references.EQUIPMENT_IDENTIFIER_GAS, equipment, "EQUIPMENT_IDENTIFIER_GAS")
        mbus_device.add(obis_references.HOURLY_GAS_METER_READING, gas_reading, "HOURLY_GAS_METER_READING")

        self.mbus_device = mbus_device

    def test_attributes(self):
        self.assertEqual(self.mbus_device.DEVICE_TYPE.value, 3)
        self.assertEqual(self.mbus_device.DEVICE_TYPE.unit, None)

        self.assertEqual(self.mbus_device.EQUIPMENT_IDENTIFIER_GAS.value,
                         '4730303339303031393336393930363139')
        self.assertEqual(self.mbus_device.EQUIPMENT_IDENTIFIER_GAS.unit, None)

        self.assertEqual(self.mbus_device.HOURLY_GAS_METER_READING.value, Decimal('246.138'))
        self.assertEqual(self.mbus_device.HOURLY_GAS_METER_READING.unit, 'm3')

    def test_to_json(self):
        self.assertEqual(
            json.loads(self.mbus_device.to_json()),
            {
                'CHANNEL_ID': 1,
                'DEVICE_TYPE': {'value': 3, 'unit': None},
                'EQUIPMENT_IDENTIFIER_GAS': {'value': '4730303339303031393336393930363139', 'unit': None},
                'HOURLY_GAS_METER_READING': {'datetime': '2020-04-26T20:30:01+00:00', 'value': 246.138, 'unit': 'm3'}}
        )

    def test_str(self):
        self.assertEqual(
            str(self.mbus_device),
            (
                'MBUS DEVICE (channel 1)\n'
                '\tDEVICE_TYPE: 	 3	[None]\n'
                '\tEQUIPMENT_IDENTIFIER_GAS: 	 4730303339303031393336393930363139	[None]\n'
                '\tHOURLY_GAS_METER_READING: 	 246.138	[m3] at 2020-04-26T20:30:01+00:00\n'
            )
        )
