import serial
import csv
import time
from datetime import datetime

ser = serial.Serial('COM3', 9600, timeout=1)

time.sleep(2)

try:
    with open('my_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Create clear headers for all your sensor outputs
        writer.writerow(['timestamp', 'PIR_Motion', 'Accel_X', 'Accel_Y', 'Accel_Z'])
        
        while True: 
            # Read a line of data from the Arduino
            line = ser.readline().decode('utf-8').strip()
            
            if line: # Only process if we actually got data (ignores empty timeouts)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] # Friendly YYYY-MM-DD HH:MM:SS.ms format
                
                # Split the comma-separated line into individual values
                sensor_values = line.split(',')
                
                # Ensure we got all 4 expected values from the Arduino before saving
                if len(sensor_values) == 4:
                    writer.writerow([timestamp] + sensor_values)
                    f.flush() # Forces Python to save the data immediately so you don't lose anything
                    
except KeyboardInterrupt:
    print("\nData collection stopped by user. CSV file saved successfully!")
finally:
    ser.close() # Safely close the serial port