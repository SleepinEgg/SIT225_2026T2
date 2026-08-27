// Add sensor library
#include <Arduino_LSM6DS3.h>

// PIN setup
#define PIR_PIN 2      // PIR sensor signal connected to Pin 
#define RED_LED_PIN 4      // LED   

// data filtering (Accelerometer Moving Average) ---
const int numReadings = 5;       // Smooth across 5 readings
float readingsX[numReadings];    
float readingsY[numReadings];
float readingsZ[numReadings];
int readIndex = 0;               // Index of current reading

float totalX = 0, totalY = 0, totalZ = 0;
float avgX = 0, avgY = 0, avgZ = 0;

// ACCELEROMETER ALARM THRESHOLD
const float movementThreshold = 0.3;


void setup() {
  // Initialize Serial communication at 9600 baud rate
  Serial.begin(9600);
  
  // Init PIR Sensor
  pinMode(PIR_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  
  // Init Accelerometer
  if (!IMU.begin()) {
    Serial.println("Error: LSM6DS3 IMU accelerometer not detected!");
    while (1);
  }

  // Initialize all moving average array readings to 0
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readingsX[thisReading] = 0;
    readingsY[thisReading] = 0;
    readingsZ[thisReading] = 0;
  }
}



void loop() {
  // 1. Read PIR Sensor (Outputs 0 or 1)
  int pirValue = digitalRead(PIR_PIN);

  // 2. Read LSM6DS3 Accelerometer data
  float rawX = 0, rawY = 0, rawZ = 0;
  
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(rawX, rawY, rawZ);
  }

  // 3. Data Quality Check: Filter out accelerometer anomalies > 16g
  if (abs(rawX) <= 16.0 && abs(rawY) <= 16.0 && abs(rawZ) <= 16.0) { 
    
    // Subtract the oldest reading from running total
    totalX -= readingsX[readIndex];
    totalY -= readingsY[readIndex];
    totalZ -= readingsZ[readIndex];
    
    // Read new values into the array
    readingsX[readIndex] = rawX;
    readingsY[readIndex] = rawY;
    readingsZ[readIndex] = rawZ;
    
    // Add new reading to running total
    totalX += readingsX[readIndex];
    totalY += readingsY[readIndex];
    totalZ += readingsZ[readIndex];
    
    // Advance to next position in array
    readIndex++;
    if (readIndex >= numReadings) {
      readIndex = 0;
    }
    
    // Calculate final smoothed averages (in g)
    avgX = totalX / numReadings;
    avgY = totalY / numReadings;
    avgZ = totalZ / numReadings;
  }

  // 4. Check Alarm Conditions
  // Calculate current orientation differs from rest.
  bool motionDetected = (pirValue == 1);
  bool forceDetected = (abs(avgX) > movementThreshold || 
                        abs(avgY) > movementThreshold || 
                        abs(abs(avgZ) - 1.0) > movementThreshold);

  if (motionDetected || forceDetected) {
    digitalWrite(RED_LED_PIN, HIGH);
  } else {
    digitalWrite(RED_LED_PIN, LOW);
  }

  // 5. Print Data to Serial (Processed by Python)
  // Format: PIR,AccelX,AccelY,AccelZ
  Serial.print(pirValue);
  Serial.print(",");
  Serial.print(avgX, 3); 
  Serial.print(",");
  Serial.print(avgY, 3);
  Serial.print(",");
  Serial.println(avgZ, 3);

  // 5. 200ms delay to make the loop run 5 times per sec
  delay(200);
}