#include <OneWire.h>
#include <DallasTemperature.h>

OneWire oneWire(6);  // Setup an instance to communicate with any 1-Wire devices
DallasTemperature sensors(&oneWire);

DeviceAddress sensor1 = {0x28, 0x94, 0x9F, 0x73, 0x3A, 0x19, 0x01, 0x3F}; // Temp sensor address sensor 1
DeviceAddress sensor2 = {0x28, 0xA0, 0x7E, 0x96, 0xF0, 0x01, 0x3C, 0x31}; // Temp sensor address sensor 1

void setup() {
  Serial.begin(9600);
  sensors.begin();
    if(!sensors.getAddress(sensor1, 0)) {
    Serial.println("Error: Check sensor connections!");
    while(0);  //don't forget change to while(1)
  }
}

void loop() {
  sensors.requestTemperatures();
  float temp_1 = sensors.getTempC(sensor1); //first sensor
  float temp_2 = sensors.getTempC(sensor2);  // secound sensor
  //Serial.print("TT1:");
  Serial.print(temp_1);
  //Serial.print(";TT2:");
  Serial.print(";");
  Serial.println(temp_2);
  delay(1000);
}