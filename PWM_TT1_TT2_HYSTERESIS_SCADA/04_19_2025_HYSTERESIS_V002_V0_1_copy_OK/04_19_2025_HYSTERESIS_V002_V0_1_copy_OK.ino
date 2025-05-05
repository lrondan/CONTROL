/*
******************************************************************
 * Vanguard Community College
 * School of Engineering
 * Sketch: 04_14_2025_PWM
 * Date: 15 April 2025
 * This programs is for a small process control trainer
 * It has a process vessel two temperature sensors a Circulation pump 
 * a heat exhanger which function as a cooler and a fan to increase 
 * the cooling capacity of the heat exchanger
 * 
 * The additional sofware library used are OneWire for readng multiple 
 * temparature sensors and I2C for short distance communication
 * 
 * If you are using more I2C devices using the Wire library use lcd.begin(false)
 * this stops the library(LCD_I2C) from calling Wire.begin()
******************************************************************
*/

#define VCC_001_01 // Read serialnumber from label and change (003) accordingly
#include "common.h"

//sensor flow vars
volatile int flow_frequency;
unsigned int flowRate;
unsigned long cloopTime;
unsigned long currentTime;

//START HYSTERESIS CONFIG
const float T_SP = 40.0;  //SETPOINT
const float HYSTERESIS = 2.0;  //(+-2)
//END HYSTERESIS CONFIG

//pulse count for flowsens
void flow(){
  flow_frequency++;
}

void setup() {
  // Configure pinmodes as output
  pinMode(HEAT1PIN, OUTPUT);     // HEATER 1
  pinMode(PUMP1PIN, OUTPUT);     // PUMP 1
  pinMode(PUMP2PIN, OUTPUT);     // PUMP 2
  pinMode(COOL1PIN, OUTPUT);     // COOLER 1
  // Configure pinmodes as input
  pinMode(FLOW1PIN, INPUT);    // FLOW 1
  digitalWrite(FLOW1PIN, HIGH);
  Serial.begin(9600);
  attachInterrupt(0, flow, RISING);  //interrupts for flow sensor
  TEMP_SENS.begin();
}

void loop() {
  TEMP_SENS.requestTemperatures();
  double TEMP_TT1 = TEMP_SENS.getTempC(ADDR_TT1); // GET DATA FROM TT1
  double TEMP_TT2 = TEMP_SENS.getTempC(ADDR_TT2); // GET DATA FROM TT2
  //flowRate equations
  currentTime = millis();
  if (currentTime >= (cloopTime + 1000)) {
    cloopTime = currentTime;
    flowRate = (flow_frequency / 7.5) -2 ;  //YF-S201 MODEL  (L/ min)
    flow_frequency = 0;
    }
  //logic
  bool needsCooling = (TEMP_TT1 > (T_SP + HYSTERESIS)) || (TEMP_TT2 > (T_SP + HYSTERESIS));
  bool needsHeating = (TEMP_TT1 < (T_SP - HYSTERESIS)) || (TEMP_TT2 < (T_SP - HYSTERESIS));
  //control
  digitalWrite(HEAT1PIN, needsHeating ? HIGH : LOW);
  digitalWrite(COOL1PIN, needsCooling ? HIGH : LOW);
  //PUMP1
  digitalWrite(PUMP1PIN, (needsCooling || needsHeating) ? ON : OFF);
  //Serial
  Serial.print("Temp1: "); Serial.print(TEMP_TT1);
  Serial.print(" | Temp2: "); Serial.print(TEMP_TT2);
  Serial.print(" | Flow: "); Serial.print(flowRate); Serial.print(" L/min");
  Serial.print(" | Heater: "); Serial.print(digitalRead(HEAT1PIN));
  Serial.print(" | Cooler: "); Serial.print(digitalRead(COOL1PIN));
  Serial.print(" | Pump: "); Serial.println(digitalRead(PUMP1PIN));
  
  delay(500);
}
