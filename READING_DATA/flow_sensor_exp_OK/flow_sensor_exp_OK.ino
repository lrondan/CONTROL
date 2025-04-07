#define FlowPin 2
volatile int pulseCount = 0;
float flowRate = 0;
float totalFlow = 0;
const float pulsesPerLiter = 450.0; // Adjust based on datasheet

void setup() {
  pinMode(FlowPin, INPUT);
  Serial.begin(9600);
  attachInterrupt(digitalPinToInterrupt(2), countPulse, RISING); // Pin 2 = interrupt
}

void loop() {
  flowRate = (pulseCount / pulsesPerLiter) * 60; // L/min (if measured over 1 sec)
  totalFlow += (pulseCount / pulsesPerLiter);
  pulseCount = 0; // Reset counter
  Serial.print("Flow Rate: ");
  Serial.print(flowRate);
  Serial.println(" L/min");
  delay(1000);
}

void countPulse() {
  pulseCount++;
}
