// Define Pins for HC-SR04 Ultrasonic Sensor
#define TRIG_PIN 9
#define ECHO_PIN 10

// Variables to store duration and distance
long duration;
float distance_cm;

void setup() {
  // Set baud rate for serial communication
  Serial.begin(9600);

  // Set pin modes for trigger and echo pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  // Clear the TRIG_PIN
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  // Set the TRIG_PIN HIGH for 10 microseconds to send sonic pulse
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read the ECHO_PIN, returns travel time in microseconds
  duration = pulseIn(ECHO_PIN, HIGH);

  // Calculate distance in centimeters (speed of sound = 0.0343 cm/us)
  distance_cm = duration * 0.0343 / 2;

  // Print single distance value to serial port for Python
  Serial.println(distance_cm);

  // Wait a bit before taking the next reading
  delay(1000);
}