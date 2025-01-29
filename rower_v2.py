import asyncio
import time
import csv
import struct
from bleak import BleakScanner, BleakClient

# UUID for Concept2 PM5 rowing data characteristic
ROWING_CHARACTERISTIC_UUID = "CE060031-43E5-11E4-916C-0800200C9A66"

# File paths
RAW_DATA_FILE = "rowing_data_raw.csv"
TRANSLATED_DATA_FILE = "rowing_data_translated.csv"

def parse_rowing_data(raw_data):
    """
    Parses the raw byte array into meaningful rowing statistics.
    Args:
        raw_data (str): A string representation of the bytearray (e.g., "bytearray(b'\xa4#?\xcfpr\xc2\n\xa2[i\xff')").
    Returns:
        dict: A dictionary with parsed rowing data.
    """
    try:
        # Convert the string back to a byte array
        raw_data = eval(raw_data)  # Convert "bytearray(...)" string back to a Python object
        if isinstance(raw_data, bytearray):
            raw_data = bytes(raw_data)

        # Parse the data based on the known format
        stroke_state = raw_data[0]  # 1 byte
        stroke_rate = raw_data[1]  # 1 byte
        distance = int.from_bytes(raw_data[2:5], byteorder='little')  # 3 bytes
        elapsed_time = int.from_bytes(raw_data[5:7], byteorder='little') / 100  # 2 bytes, in seconds
        power = int.from_bytes(raw_data[7:9], byteorder='little')  # 2 bytes
        calories = int.from_bytes(raw_data[9:11], byteorder='little')  # 2 bytes

        # Return parsed data as a dictionary
        return {
            "stroke_state": stroke_state,
            "stroke_rate": stroke_rate,
            "distance_meters": distance,
            "elapsed_time_seconds": elapsed_time,
            "power_watts": power,
            "calories_burned": calories
        }
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None


async def scan_for_pm5():
    """Scan for BLE devices and find the Concept2 PM5."""
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found device: {device.name} - {device.address}")
        if "PM5" in (device.name or ""):
            print(f"PM5 found: {device.name} - {device.address}")
            return device.address
    print("PM5 not found. Ensure it is powered on and in Bluetooth mode.")
    return None


async def connect_and_collect_data(address):
    """Connect to the PM5 and collect rowing data."""
    print(f"Connecting to PM5 at {address}...")
    async with BleakClient(address) as client:
        print(f"Connected to PM5: {address}")
        
        # Open both CSV files for writing
        with open(RAW_DATA_FILE, mode="w", newline="") as raw_file, open(TRANSLATED_DATA_FILE, mode="w", newline="") as translated_file:
            raw_writer = csv.writer(raw_file)
            translated_writer = csv.DictWriter(translated_file, fieldnames=[
                "Timestamp", 
                "stroke_state", 
                "stroke_rate", 
                "distance_meters", 
                "elapsed_time_seconds", 
                "power_watts", 
                "calories_burned"
            ])
            # Write headers
            raw_writer.writerow(["Timestamp", "Raw Data"])
            translated_writer.writeheader()

            try:
                print("Collecting rowing data. Press Ctrl+C to stop.")
                while True:
                    # Read raw data
                    raw_data = await client.read_gatt_char(ROWING_CHARACTERISTIC_UUID)
                    timestamp = time.time()
                    print(f"Raw Data: {raw_data}")

                    # Save raw data to file
                    raw_writer.writerow([timestamp, raw_data])

                    # Parse and save translated data
                    parsed_data = parse_rowing_data(str(raw_data))
                    if parsed_data:
                        parsed_data["Timestamp"] = timestamp
                        translated_writer.writerow(parsed_data)

                    await asyncio.sleep(0.1)  # Adjust the frequency of reading as needed
            except asyncio.CancelledError:
                print("Data collection stopped.")
            except Exception as e:
                print(f"Error during data collection: {e}")


async def main():
    """Main function to scan, connect, and collect data."""
    # Scan for PM5
    address = await scan_for_pm5()
    if not address:
        return

    # Connect and collect data
    try:
        await connect_and_collect_data(address)
    except KeyboardInterrupt:
        print("Program terminated by user.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript stopped.")
