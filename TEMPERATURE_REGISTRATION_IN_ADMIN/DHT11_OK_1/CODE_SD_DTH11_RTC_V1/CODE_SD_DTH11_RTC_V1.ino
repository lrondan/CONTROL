#include <SimpleDHT.h>
#include <RTClib.h>
#include <SPI.h>
#include <SD.h>

#define DHT_PIN 2          // Pin DHT11

SimpleDHT11 dht11(DHT_PIN);

RTC_DS3231 rtc;           //  RTC obect

const int chipSelect = 10; // Pin CS SD READER

void setup() {
  Serial.begin(9600);

  // START RTC
  if (!rtc.begin()) {
    Serial.println("Error: RTC not found");
    while (1);
  }

  // 
  if (rtc.lostPower()) {
    Serial.println("RTC loss energy, updating time...");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  // Start SD
  if (!SD.begin(chipSelect)) {
    Serial.println("Error: SD Card not found");
    return;
  }
  Serial.println("System ready");
}

void loop() {
  byte temperature = 0;
  byte humidity = 0;
  // read data from DHT11
  int err = SimpleDHTErrSuccess;
  if ((err = dht11.read(&temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    Serial.print("Read failed, err="); 
    Serial.println(err);
    delay(2000);
    return;
  }

  // test the read
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error to read data from DHT11");
    return;
  }

  // get date and time from RTC
  DateTime now = rtc.now();

  // Open the file
  File dataFile = SD.open("datalog.csv", FILE_WRITE);

  if (dataFile) {
    // write data in CSV format: Date, Hour, Temperature, Humidity
    dataFile.print(now.year()); dataFile.print("/");
    dataFile.print(now.month()); dataFile.print("/");
    dataFile.print(now.day()); dataFile.print(",");
    dataFile.print(now.hour()); dataFile.print(":");
    dataFile.print(now.minute()); dataFile.print(":");
    dataFile.print(now.second()); dataFile.print(",");
    dataFile.print(temperature); dataFile.print(",");
    dataFile.println(humidity);
    dataFile.close();

    Serial.print("Data Saved: ");
    Serial.print(now.timestamp(DateTime::TIMESTAMP_FULL));
    Serial.print(", Temp: "); Serial.print(temperature);
    Serial.print("°C, Hum: "); Serial.print(humidity); Serial.println("%");
  } else {
    Serial.println("Error to write the file");
  }

  delay(6000); // Wait _6_ s between mesuretments
}