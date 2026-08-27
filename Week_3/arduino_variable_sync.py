"""
    Requirement: arduino_iot_cloud
    Install: pip install arduino-iot-cloud

    @Ahsan Habib
    School of IT, Deakin University, Australia.
"""

import sys
import traceback
import random
from arduino_iot_cloud import ArduinoCloudClient
import asyncio
from datetime import datetime

DEVICE_ID = "d0b51817-7e52-40c0-9f36-1cdaca6cd1b6"
SECRET_KEY = "O2pQdmzV6bh2CncQe?twGmnZJ"


# Callback function on temperature change event.
# 
def on_temperature_changed(client, value):
    global log_file
    print(f"New temperature: {value}")
    
    if log_file:
        try:
            # a. Get current timestamp (formatted cleanly: YYYY-MM-DD HH:MM:SS)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # b. Create the CSV string
            csv_line = f"{timestamp},{value}\n"
            
            # c. & d. Write the string and flush immediately to ensure it saves to disk
            log_file.write(csv_line)
            log_file.flush() 
            
        except Exception as e:
            print(f"Error writing to log file: {e}")



def main():
    global log_file
    print("main() function")

    log_file = open("temperature_log.csv", mode="a", encoding="utf-8", newline='')

    if log_file.tell() == 0:
            log_file.write("Timestamp,Temperature\n")
            log_file.flush()



    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Register with 'temperature' cloud variable
    # and listen on its value changes in 'on_temperature_changed'
    # callback function.

    client.register(
        "temperature", value=None, 
        on_write=on_temperature_changed)

    # start cloud client
    try:
        client.start()
    finally:
        # 5. Clean closure: Ensure the file is safely closed when script stops
        if log_file:
            print("\nClosing log file safely...")
            log_file.close()


if __name__ == "__main__":
    try:
        main()  # main function which runs in an internal infinite loop
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_type, file=print)
        