#include <SimpleDHT.h>

#define DHT_PIN 4  // The pin connected to DHT11 data line

SimpleDHT11 dht11(DHT_PIN);

void setup() {
  Serial.begin(9600);
}

void loop() {
  // Read without samples (simplest way)
  byte temperature = 0;
  byte humidity = 0;
  
  int err = SimpleDHTErrSuccess;
  if ((err = dht11.read(&temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    Serial.print("Read failed, err="); 
    Serial.println(err);
    delay(2000);
    return;
  }
  
  Serial.print("Humidity: ");
  Serial.print((int)humidity);
  Serial.print("% | Temp: ");
  Serial.print((int)temperature);
  Serial.println("°C");
  
  delay(2000);  // Wait 2 seconds between readings
}