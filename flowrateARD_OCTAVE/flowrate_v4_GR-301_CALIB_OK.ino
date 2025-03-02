/*
################# GR-201 FS ###################
################ by: Rondan ###################
###############################################
*/

const int sensorPin = 2;       // Yellow wire is connected in Pin 2
const float factorK = 2013.88;   // The calibration factor of the sensor, number of pulses per liter

// Variables
volatile int pulseCount = 0;   // Counts the number of pulses
float flowRate = 0.0;          // Start flowrate en L/min
float totalFlow = 0.0;         // Satrt accumultes the total volume of liquid thad has passed
unsigned long oldTime = 0;     // Start last time (use for timing)

// Function pulse Counter
void pulseCounter() {
  pulseCount++;  // Increase the number of pulses
}

void setup() {
  // Start serial
  Serial.begin(9600);

  // Config sensor Pin as INPUT
  pinMode(sensorPin, INPUT);

  // Interrupts for pulses
  attachInterrupt(digitalPinToInterrupt(sensorPin), pulseCounter, FALLING);
}

void loop() {
  // Get the time
  unsigned long currentTime = millis();

  // Flowrate per secound
  if (currentTime - oldTime >= 1000) {

    detachInterrupt(digitalPinToInterrupt(sensorPin));

    // Convert flowrate in (L/min)
    flowRate = (pulseCount / factorK) * 60;

    // Total Volumen in L
    totalFlow += (pulseCount / factorK);

    // Display the data
    //Serial.print("FlowRate: ");
    Serial.print(flowRate);
    Serial.print(',');
    //Serial.print(" L/min | Total Vol: ");
    Serial.println(totalFlow);
    //Serial.println(" L");
    if (flowRate > 0){
      unsigned long startTime = millis();
      
      //Serial.print("time (s): ");
      //Serial.print(startTime / 1000);
      //Serial.println(" s");
    }


    // Restart the counter
    pulseCount = 0;
    oldTime = currentTime;

    // Restart the interrupts
    attachInterrupt(digitalPinToInterrupt(sensorPin), pulseCounter, FALLING);
  }
}