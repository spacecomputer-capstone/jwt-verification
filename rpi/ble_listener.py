"""
Legacy development/testing helper.

This BLE listener was used during earlier experiments for receiving JWTs over
Bluetooth. It is not part of the current workflow because the active flow uses
HTTP between the app, Pi bridge, and backend instead.
"""

import asyncio
from bleak import BleakGATTCharacteristic, BleakGATTServiceCollection
from bleak.backends.bluezdbus.server import (
    BleakGATTServer,
    BleakGATTService,
    BleakGATTCharacteristic
)

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID    = "12345678-1234-5678-1234-56789abcdef1"

class JWTServer:
    def __init__(self, on_token_callback):
        self.on_token_callback = on_token_callback

    async def start(self):
        service = BleakGATTService(SERVICE_UUID)
        char = BleakGATTCharacteristic(
            CHAR_UUID,
            ["write"],
            write=self._on_write
        )
        service.add_characteristic(char)
        self.server = BleakGATTServer()
        self.server.add_service(service)
        await self.server.start()
        print("BLE server started. Waiting for JWT...")

        while True:
            await asyncio.sleep(3600)

    def _on_write(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        token = data.decode()
        print("Received JWT via BLE")
        self.on_token_callback(token)
