https://github.com/M4tth4ck333/bleak
import asyncio
from bleak import BleakScanner, BleakClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BLE_Manager")

class BLEManager:
    def __init__(self):
        self.scanner = BleakScanner()
        self.connected_devices = {}

    async def scan_for_devices(self):
        """Scans for nearby Bluetooth devices."""
        logger.info("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        for d in devices:
            logger.info(f"Found device: {d.name} [{d.address}]")
        return devices

    async def connect_to_device(self, address):
        """Connects to a specific BLE device (e.g., AR-XAI module or 3D Printer)."""
        logger.info(f"Attempting to connect to {address}...")
        client = BleakClient(address)
        try:
            await client.connect()
            self.connected_devices[address] = client
            logger.info(f"Connected to {address}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {address}: {e}")
            return False

    async def disconnect_from_device(self, address):
        """Disconnects from a device."""
        if address in self.connected_devices:
            client = self.connected_devices[address]
            await client.disconnect()
            del self.connected_devices[address]
            logger.info(f"Disconnected from {address}")

async def main():
    manager = BLEManager()
    # In a real environment, we would scan and connect.
    # For this skeleton, we just demonstrate the call structure.
    devices = await manager.scan_for_devices()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        # Expected to fail in environments without Bluetooth adapters
        print(f"Bluetooth Error (expected in some sandboxes): {e}")
