#include <OneWire.h>
#include <DallasTemperature.h>

OneWire oneWire(6);  // Setup an instance to communicate with any 1-Wire devices
DallasTemperature sensors(&oneWire);

DeviceAddress sensor1 = {0x28, 0x94, 0x9F, 0x73, 0x3A, 0x19, 0x01, 0x3F}; // Temp sensor address

void setup() {
  Serial.begin(9600);
  sensors.begin();
    if(!sensors.getAddress(sensor1, 0)) {
    Serial.println("Error: Check sensor connections!");
    while(1);  //don't forget change to while(1)
  }
}

void loop() {
  float tempC = sensors.getTempC(sensor1); //first sensor
  //Serial.print("Temperature: ");
  Serial.println(tempC);
  //Serial.println("°C");
  delay(1000);
}