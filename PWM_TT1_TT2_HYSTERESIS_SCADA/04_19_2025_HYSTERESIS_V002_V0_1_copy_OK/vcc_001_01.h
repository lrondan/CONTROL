
/*  Inlcude file for VSEN______ process trainer serial number ____
    In this file define only hardware addresses, and specific arduino ports to be used
*/

#ifdef VCC_001_01
  // Arduino UNO as Microcontroller
  /* Assign OneWire Address */
  uint8_t ADDR_TT1[8] = {0x28, 0x81, 0x8E, 0x53, 0x3A, 0x19, 0x01, 0x4E}; // Temp sensor TT1
  uint8_t ADDR_TT2[8] = {0x28, 0x32, 0xA0, 0x5B, 0x3A, 0x19, 0x01, 0x56}; // Temp sensor TT2
  #define HEAT1PIN     9  // Heater is activated from Arduino UNO pin 9
  #define PUMP1PIN     4  // Pump 1 is activated from Arduino UNO pin 3
  #define PUMP2PIN     6  // Pump 2 is activated from Arduino UNO pin 5
  #define COOL1PIN     5  // Fan  1 is activared from Arduino UNO pin 6
  unsigned char FLOW1PIN = 2;  // Read data from flow sensor 1
  #define ONE_WIRE_BUS 8  // 1-Wire two devices in total  --YELLOW 
  //LCD_I2C lcd1(0x27);     // Setup and instance to communicate with LCD
  //OneWire oneWire(ONE_WIRE_BUS);  // Setup an instance to communicate with any 1-Wire devices  
  //DallasTemperature TEMP_SENS(&oneWire);
  #define ON HIGH
  #define OFF LOW

#endif