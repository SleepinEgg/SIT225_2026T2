import csv
from datetime import datetime
import os
from arduino_iot_cloud import ArduinoCloudClient


DEVICE_ID = "98d93ae9-1ddc-42fa-818c-2720a66c493a"
SECRET_KEY = "GbyR0MHokilIKyAQMwu3jsGv@"


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

client = ArduinoCloudClient(
    device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
)

latest_readings = {"x": None, "y": None, "z": None}


def on_axis_update(client, value, axis_name):
    timestamp = datetime.now().isoformat()
    latest_readings[axis_name] = value

    #  Write to individual file
    file_path_indiv = os.path.join(
        SCRIPT_DIR, f"accelerometer_{axis_name}.csv"
    )
    with open(file_path_indiv, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, value])
        f.flush()

    # Step 4: Write to combined file
    if all(val is not None for val in latest_readings.values()):
        file_path_comb = os.path.join(SCRIPT_DIR, "accelerometer_combined.csv")
        with open(file_path_comb, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    timestamp,
                    latest_readings["x"],
                    latest_readings["y"],
                    latest_readings["z"],
                ]
            )
            f.flush()

    print(
        f"Logged {axis_name.upper()}: {value} -> Saved to {file_path_indiv}"
    )


# Register callbacks
client.register(
    "python_x", on_write=lambda c, v: on_axis_update(c, v, "x")
)
client.register(
    "python_y", on_write=lambda c, v: on_axis_update(c, v, "y")
)
client.register(
    "python_z", on_write=lambda c, v: on_axis_update(c, v, "z")
)

print("Listening for smartphone stream...")
client.start()