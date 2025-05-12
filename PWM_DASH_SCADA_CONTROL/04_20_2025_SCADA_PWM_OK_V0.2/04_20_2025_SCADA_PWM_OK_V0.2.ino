// SCADA_Industrial_Controller.ino
#include <OneWire.h>
#include <DallasTemperature.h>

// OneWire Setup
const int ONE_WIRE_BUS = 8;          // Data wire for temp sensors
OneWire oneWire(ONE_WIRE_BUS);       // Setup OneWire instance
DallasTemperature sensors(&oneWire); // Pass to DallasTemperature

// PWM Outputs
const int PUMP_PIN = 6;     // PWM for pump (0-255)
const int COOLER_PIN = 11;   // PWM for cooler fan (0-255)
const int HEATER_PIN = 9;   // Triac control for heater (0-180° phase control)

// Timing
unsigned long lastUpdate = 0;
const long interval = 1000;  // Update interval (ms)

void setup() {
  // Initialize outputs
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(COOLER_PIN, OUTPUT);
  pinMode(HEATER_PIN, OUTPUT);
  
  // Start OneWire sensors
  sensors.begin();
  
  // Start serial communication
  Serial.begin(115200);
  Serial.println("SCADA Industrial Controller Ready");
}

void loop() {
  // Process serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    
    // Pump control (PWM)
    if (command.startsWith("PUMP;")) {
      int pwmValue = command.substring(5).toInt();
      pwmValue = constrain(pwmValue, 0, 255);
      analogWrite(PUMP_PIN, pwmValue);
      Serial.print("Pump set to: "); Serial.println(pwmValue);
    }
    
    // Cooler control (PWM)
    else if (command.startsWith("COOLER;")) {
      int pwmValue = command.substring(7).toInt();
      pwmValue = constrain(pwmValue, 0, 255);
      analogWrite(COOLER_PIN, pwmValue);
      Serial.print("Cooler set to: "); Serial.println(pwmValue);
    }
    
    // Heater control (Triac phase angle)
    else if (command.startsWith("HEATER;")) {
      int angle = command.substring(7).toInt();
      angle = constrain(angle, 0, 180);
      
      // Convert phase angle to time delay (simplified)
      int triacDelay = map(angle, 0, 180, 8000, 100);  // Adjust for 50/60Hz
      // In real implementation, use interrupt and zero-cross detection
      analogWrite(HEATER_PIN, angle);  // Simplified for demo
      
      Serial.print("Heater angle set to: "); Serial.println(angle);
    }
  }

  // Send temperature data at fixed interval
  if (millis() - lastUpdate >= interval) {
    sensors.requestTemperatures(); // Send command to all sensors
    
    float temp1 = sensors.getTempCByIndex(0); // Sensor 1
    float temp2 = sensors.getTempCByIndex(1); // Sensor 2
    
    Serial.print("DATA;");
    Serial.print(temp1); Serial.print(";");
    Serial.print(temp2); Serial.print(";");
    Serial.println(millis());
    
    lastUpdate = millis();
  }
}