#include "vsen022_common.h"

// lcd init
void setupLCD() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(2, 0);
  lcd.print("Vanguard College");
  lcd.setCursor(1, 1);
  lcd.print("Engineering School");
  lcd.setCursor(4, 2);
  lcd.print("VSEN-022-002");
  lcd.setCursor(1, 3);
  lcd.print("Process Controller");
  delay(20);
  lcd.clear();  // clear display
}

// function to update the data
void updateLCD() {
  lcd.clear();  // clear the previous data
  
  // Line 1
  lcd.setCursor(0, 0);
  lcd.print("TT1:");lcd.print(temp1);
  lcd.setCursor(14, 0);
  lcd.print("C:"); lcd.print((Output < 0) ? abs(Output) : 0);
  
  // Line 2
  lcd.setCursor(0, 1);
  lcd.print("TT2:");lcd.print(temp2);
  lcd.setCursor(14, 1);
  lcd.print("H:"); lcd.print((Output > 0) ? Output : 0);
  
  // Line 3
  lcd.setCursor(0, 2);
  lcd.print("FT1:");lcd.print(flowRate);
  lcd.setCursor(14, 2);
  int pump_perc = analogRead(PUMP_PIN);
  lcd.print("P:"); lcd.print(pump_perc);
  
  //Line 4
  lcd.setCursor(0, 3);
  lcd.print("P:");        lcd.print(Kp);
  lcd.setCursor(7, 3);
  lcd.print("I:");        lcd.print(Ki);
  lcd.setCursor(14, 3);
  lcd.print("D:");        lcd.print(Kd);
}

void zeroCrossISR(){
  zero_cross = true;
  digitalWrite(HEATER_TRIAC, LOW);
  if (power > 0){
  delayMicroseconds(delay_Time);
  digitalWrite(HEATER_TRIAC, HIGH);
  delayMicroseconds(100);
  digitalWrite(HEATER_TRIAC, LOW);
  }
  zero_cross = false;
}

void pulseCounter(){
  pulseCount++;
}

void calculateFlow() {
  if(millis() - oldTime > 1000) {
    detachInterrupt(FLOW_SENSOR);
    flowRate = (pulseCount * 2.25) / 70.0; // Calibration factor for YF-S201
    pulseCount = 0;
    oldTime = millis();
    attachInterrupt(FLOW_SENSOR, pulseCounter, FALLING);
  }
}

void setup() {
  setupLCD();  // start LCD
  Serial.begin(9600);
  sensors.begin();
    if(!sensors.getAddress(sensor1, 0) || !sensors.getAddress(sensor2, 1)) {
    Serial.println("Error: Check sensor connections!");
    while(0);  //don't forget change to while(1)
  }
  // PID Setup
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-100, 100);
  
  // Pin modes
  pinMode(COOLER_PIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(HEATER_TRIAC, OUTPUT);
  pinMode(ZeroCrossPin, INPUT_PULLUP);
  pinMode(FLOW_SENSOR, INPUT_PULLUP);

  //Flow sensor interupt
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), pulseCounter, FALLING);

  // traic trigger interupt
  attachInterrupt(digitalPinToInterrupt(ZeroCrossPin), zeroCrossISR, RISING);
}

void loop() {
  updateLCD();  // update
  delay(1000);  // wait 1 sec between updates
  static unsigned long lastPID = millis();

    if(millis() - lastPID >= 1000) {
    // Read temperatures
    sensors.requestTemperatures();
    temp1 = sensors.getTempC(sensor1);
    temp2 = sensors.getTempC(sensor2);
    Input = (temp1 + temp2) / 2.0; // Average temperature
    
    // Calculate flow rate
    calculateFlow();
    
    // Compute PID
    myPID.Compute();
    controlActuators();
    
    // Send data to SCADA
    sendData();
    
    lastPID = millis();
  }
}
void controlActuators(){
  // Control cooler (ON-OFF)
  if(Output < 0) {
    analogWrite(COOLER_PIN, map(abs(Output), 0, 100, 0, 255));
    delay(100);
    digitalWrite(HEATER_TRIAC, LOW);
    delay(100);
  }
  else {
    analogWrite(COOLER_PIN, 0);
    // Simple time proportional control for TRIAC
    digitalWrite(HEATER_TRIAC, HIGH);
    delay(100);
  }
  // switch pump only if needs cooling or heating

  if (Output < 0){
    analogWrite(PUMP_PIN, map((Output), -100, 0, 100, 60));
    delay(100);
  } else{
    analogWrite(PUMP_PIN, map((Output),  0, 100, 200, 255));
    delay(100);
  }
}
void sendData() {
  Serial.print("T1:"); Serial.print(sensors.getTempC(sensor1));
  Serial.print(",T2:"); Serial.print(sensors.getTempC(sensor2));
  Serial.print(",F:"); Serial.print(flowRate);
  Serial.print(",H:"); Serial.print((Output > 0) ? Output : 0);
  Serial.print(",C:"); Serial.print((Output < 0) ? abs(Output) : 0);
  Serial.print(",S:"); Serial.println(Setpoint);
  //
  //Serial.print(Output);
}

void checkSerial() {
  if(Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if(cmd.startsWith("SETP:")) {
      Setpoint = cmd.substring(5).toFloat();
    }
    else if(cmd.startsWith("KP:")) {
      Kp = cmd.substring(3).toFloat();
      myPID.SetTunings(Kp, Ki, Kd);
    }
    else if(cmd.startsWith("KI:")) {
      Ki = cmd.substring(3).toFloat();
      myPID.SetTunings(Kp, Ki, Kd);
    }
    else if(cmd.startsWith("KD:")) {
      Kd = cmd.substring(3).toFloat();
      myPID.SetTunings(Kp, Ki, Kd);
    }
    else if(cmd == "EMSTOP") {
      digitalWrite(HEATER_TRIAC, LOW);
      digitalWrite(COOLER_PIN, 0);
      digitalWrite(PUMP_PIN, 0);
    }
  }
}
