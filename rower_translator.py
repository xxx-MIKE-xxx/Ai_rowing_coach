import csv
import struct

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


def process_csv(input_file, output_file):
    """
    Reads the input CSV file with raw data, parses it, and writes the translated data to a new CSV file.
    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to save the translated CSV file.
    """
    try:
        with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = [
                "Timestamp", 
                "stroke_state", 
                "stroke_rate", 
                "distance_meters", 
                "elapsed_time_seconds", 
                "power_watts", 
                "calories_burned"
            ]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                timestamp = row["Timestamp"]
                raw_data = row["Raw Data"]
                parsed_data = parse_rowing_data(raw_data)
                if parsed_data:
                    parsed_data["Timestamp"] = timestamp
                    writer.writerow(parsed_data)
            print(f"Processed data saved to {output_file}.")
    except Exception as e:
        print(f"Error processing CSV file: {e}")


if __name__ == "__main__":
    # Paths to input and output CSV files
    input_file = "rowing_data.csv"  # Replace with the path to your input file
    output_file = "rowing_data_translated.csv"  # Replace with the desired output file path

    # Process the input file
    process_csv(input_file, output_file)
