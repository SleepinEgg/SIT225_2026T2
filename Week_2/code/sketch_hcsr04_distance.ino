/*
    Ahsan Habib (habib@deakin.edu.au),
    School of Information Technology,
    Deakin University, Australia.
*/

const int trigger = 2;
const int echo = 3;

int getUltrasonicDistance(){
  // Function to retreive the distance reading of the ultrasonic sensor
  long duration;
  int distance;

  // Assure the trigger pin is LOW:
  digitalWrite(trigger, LOW);
  // Brief pause:
  delayMicroseconds(5);

  // Trigger the sensor by setting the trigger to HIGH:
  digitalWrite(trigger, HIGH);
  // Wait a moment before turning off the trigger:
  delayMicroseconds(10);
  // Turn off the trigger:
  digitalWrite(trigger, LOW);

  // Read the echo pin:
  duration = pulseIn(echo, HIGH);
  // Calculate the distance in centimeter (CM):
  distance = duration * 0.034 / 2;

  // Uncomment this line to return value in IN instead of CM:
  //distance = distance * 0.3937008

  // Return the distance read from the sensor:
  return distance;
}

void setup() {
  // Define inputs and outputs:
  pinMode(trigger, OUTPUT);
  pinMode(echo, INPUT);

  // Start the serial monitor:
  Serial.begin(9600);
}

void loop() {
  // Print the distance to the serial monitor:
  Serial.print("Distance: ");
  Serial.println(getUltrasonicDistance());

  // Wait one second before continuing:
  delay(1000);
}