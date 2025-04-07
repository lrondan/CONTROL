#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 8 // Data pin (DQ)

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures(); // Send command to read temp
  float tempC = sensors.getTempCByIndex(0); // 0 = first sensor
  Serial.print("Temperature: ");
  Serial.print(tempC);
  Serial.println("°C");
  delay(1000);
}