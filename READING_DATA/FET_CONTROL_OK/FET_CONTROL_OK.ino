const int motorPin = 11;  // PWM pin connected to gate

void setup() {
  pinMode(motorPin, OUTPUT);
}

void loop() {
  // Accelerate motor
  for(int speed = 0; speed <= 255; speed += 5){
    analogWrite(motorPin, speed);
    delay(100);
  }
  
  // Decelerate motor
  for(int speed = 255; speed >= 0; speed -= 5){
    analogWrite(motorPin, speed);
    delay(100);
  }
  delay(1000);  // Pause between cycles
}