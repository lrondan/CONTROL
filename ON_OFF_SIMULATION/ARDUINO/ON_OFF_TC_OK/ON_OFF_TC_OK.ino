#include <OneWire.h>
#include <DallasTemperature.h>

// DS18B20 Setup
#define ONE_WIRE_BUS 8
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// TRIAC Control
const int triacPin = 7;  // PWM pin for TRIAC trigger
float setpoint = 45.0;   // Desired temperature (°C)
const int fanPin = 9;   // fan COOLER


void setup() {
  pinMode(triacPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  sensors.begin();
  Serial.begin(9600);
}

void loop() {
  sensors.requestTemperatures();
  float temperature = sensors.getTempCByIndex(0);
  
  // Simple On/Off Control
  if (temperature < setpoint) {
    analogWrite(triacPin, 255); // Full power HEATER
    for (int i=255; i>0; i--){  // Turn off COOLER
      analogWrite(fanPin, i);
      delay(10);
    }
  } else {
    analogWrite(triacPin, 0);   // Turn off HEATER
    for (int i=0; i<255; i++){  // Turn on COOLER
      analogWrite(fanPin, i);
      delay(10);
    }
  }

  // Serial Monitor Output
  Serial.print("Temp: ");
  Serial.print(temperature);
  Serial.print("°C | Heater: ");
  Serial.print(temperature < setpoint ? "ON" : "OFF");
  Serial.print("| Cooler: ");
  Serial.println(temperature < setpoint ? "OFF" : "ON");
  delay(1000);
}
