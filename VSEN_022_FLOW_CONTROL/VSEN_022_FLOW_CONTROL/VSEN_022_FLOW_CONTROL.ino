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
  delay(2000);  // 2s
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
  int pump_value = map(FOutput, -100, 100, 255, 0);
  lcd.print("P:"); lcd.print(pump_value);
  
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

void pulseCounter(){pulseCount++;}

void setup() {
  setupLCD();  // start LCD
  Serial.begin(9600);
  sensors.begin();
    if(!sensors.getAddress(sensor1, 0) || !sensors.getAddress(sensor2, 1)) {
    Serial.println("Error: Check sensor connections!");
    while(0);  //don't forget change to while(1)
  }
  // PID Setup TEMPERATURE
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-100, 100);

  // PID FLOW
  FPID.SetMode(AUTOMATIC);
  FPID.SetOutputLimits(-100, 100);
  
  // Pin modes
  pinMode(COOLER_PIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(HEATER_TRIAC, OUTPUT);
  pinMode(ZeroCrossPin, INPUT_PULLUP);
  pinMode(FLOW_SENSOR, INPUT_PULLUP);

  //Flow sensor interupt
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), pulseCounter, RISING);
  lastTime = millis();

  // traic trigger interupt
  attachInterrupt(digitalPinToInterrupt(ZeroCrossPin), zeroCrossISR, RISING);
}

void calculateFlow() {
  unsigned long currentTime = millis();
  if(currentTime - lastTime >= 500) {
    detachInterrupt(digitalPinToInterrupt(FLOW_SENSOR));
    int count = pulseCount;
    pulseCount = 0;
    attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), pulseCounter, RISING);
    flowRate = (count / 23.0) -4; // Calibration factor for GR-301
    lastTime = currentTime;
  }
}



void loop() {
  updateLCD();  // update
  delay(500);  // wait 500 Msec between updates
  static unsigned long lastPID = millis();

    if(millis() - lastPID >= 500) {
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

    //Write data from python file
    checkSerial();
    
    lastPID = millis();
  }
}
void controlActuators(){
  // Control cooler (PWM)
  // Control heater (TRIAC)
  // Control pump (PWM)
  if(Output < 0) {
    analogWrite(COOLER_PIN, map(abs(Output), 0, 100, 0, 255));
    delay(100);
    digitalWrite(HEATER_TRIAC, LOW);
    delay(100);
  }
  else {
    analogWrite(COOLER_PIN, 0);
    digitalWrite(HEATER_TRIAC, HIGH);
    delay(100);
  }
  FInput = flowRate;
  FPID.Compute();
  analogWrite(PUMP_PIN,map(abs(FOutput), -100, 100, 0, 255));
}

void sendData() {
  Serial.print("T1:"); Serial.print(sensors.getTempC(sensor1));
  Serial.print(",T2:"); Serial.print(sensors.getTempC(sensor2));
  Serial.print(",F:"); Serial.print(flowRate);
  Serial.print(",H:"); Serial.print((Output > 0) ? Output : 0);
  Serial.print(",C:"); Serial.print((Output < 0) ? abs(Output) : 0);
  Serial.print(",S:"); Serial.print(Setpoint);
  int pump_value = map(FOutput, -100, 100, 255, 0);
  Serial.print(",P:"); Serial.println(pump_value);
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
