#include <OneWire.h>
#include <DallasTemperature.h>
#include <PID_v1.h>

// Sensor addresses (to be filled with your actual addresses)
DeviceAddress sensor1 = {0x28, 0x81, 0x8E, 0x53, 0x3A, 0x19, 0x01, 0x4E};
DeviceAddress sensor2 = {0x28, 0x32, 0xA0, 0x5B, 0x3A, 0x19, 0x01, 0x56};

// Pin definitions
#define COOLER_PIN 3    // PWM controlled fan
#define PUMP_PIN 6      // PWM controlled pump
#define HEATER_TRIAC 9   // TRIAC control (using time proportional)
#define FLOW_SENSOR 2    // Flow sensor interrupt pin

// PID Variables
double Setpoint = 30.0; // Default setpoint
double Input, Output;
double Kp=4.0, Ki=0.2, Kd=1.0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

// Flow sensor variables
volatile int pulseCount = 0;
float flowRate = 0.0;
unsigned long oldTime;

OneWire oneWire(8);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  
  // Initialize temperature sensors
  sensors.begin();
  if(!sensors.getAddress(sensor1, 0) || !sensors.getAddress(sensor2, 1)) {
    Serial.println("Error: Check sensor connections!");
    while(1);
  }
  
  // Set sensor resolution
  sensors.setResolution(sensor1, 12);
  sensors.setResolution(sensor2, 12);
  
  // PID Setup
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-100, 100);
  
  // Pin modes
  pinMode(COOLER_PIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(HEATER_TRIAC, OUTPUT);
  pinMode(FLOW_SENSOR, INPUT_PULLUP);
  
  // Flow sensor interrupt
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), pulseCounter, FALLING);
}

void loop() {
  static unsigned long lastPID = millis();
  
  if(millis() - lastPID >= 1000) {
    // Read temperatures
    sensors.requestTemperatures();
    double temp1 = sensors.getTempC(sensor1);
    double temp2 = sensors.getTempC(sensor2);
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
  
  checkSerial();
}

void pulseCounter() {
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

void controlActuators() {
  // Control pump (always on when system is running)
  analogWrite(PUMP_PIN, 255); // Full speed
  
  // Control cooler (0-100% PWM)
  if(Output < 0) {
    analogWrite(COOLER_PIN, map(abs(Output), 0, 100, 0, 255));
    digitalWrite(HEATER_TRIAC, LOW);
  } 
  // Control heater (TRIAC time proportional control)
  else {
    analogWrite(COOLER_PIN, 0);
    // Simple time proportional control for TRIAC
    unsigned long windowStart = millis();
    unsigned long windowSize = 1000; // 1 second window
    unsigned long onTime = map(Output, 0, 100, 0, windowSize);
    
    if((millis() - windowStart) < onTime) {
      digitalWrite(HEATER_TRIAC, HIGH);
    } else {
      digitalWrite(HEATER_TRIAC, LOW);
    }
  }
}

void sendData() {
  Serial.print("T1:"); Serial.print(sensors.getTempC(sensor1));
  Serial.print(",T2:"); Serial.print(sensors.getTempC(sensor2));
  Serial.print(",F:"); Serial.print(flowRate);
  Serial.print(",H:"); Serial.print((Output > 0) ? Output : 0);
  Serial.print(",C:"); Serial.print((Output < 0) ? abs(Output) : 0);
  Serial.print(",S:"); Serial.println(Setpoint);
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
      analogWrite(COOLER_PIN, 0);
      analogWrite(PUMP_PIN, 0);
    }
  }
}
