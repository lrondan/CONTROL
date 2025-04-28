#include <PID_v1.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Pines
#define HEATER_PIN 3
#define COOLER_PIN 5
#define PUMP_PIN 7
#define FLOW_SENSOR 2

// Configuración sensores de temperatura
OneWire oneWire(8);
DallasTemperature sensors(&oneWire);
DeviceAddress tempSensor1, tempSensor2;

// Variables PID
double Setpoint = 50.0;
double Input, Output;
PID myPID(&Input, &Output, &Setpoint, 2.0, 0.1, 0.5, DIRECT);

// Variables de flujo
volatile int flowPulses = 0;
float flowRate = 0.0;
unsigned long oldTime;

void flowISR() {
  flowPulses++;
}

void setup() {
  Serial.begin(115200);
  
  // Inicializar sensores de temperatura
  sensors.begin();
  sensors.getAddress(tempSensor1, 0);
  sensors.getAddress(tempSensor2, 1);
  
  // Configurar PID
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-100, 100);
  
  // Configurar pines
  pinMode(HEATER_PIN, OUTPUT);
  pinMode(COOLER_PIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(FLOW_SENSOR, INPUT_PULLUP);
  
  // Interrupción sensor de flujo
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), flowISR, FALLING);
  
  digitalWrite(PUMP_PIN, HIGH); // Activar bomba
}

void loop() {
  static unsigned long lastPID = millis();
  
  // Actualizar temperatura cada segundo
  if (millis() - lastPID >= 1000) {
    updateTemperatures();
    calculateFlow();
    computePID();
    controlActuators();
    sendDataToSCADA();
    lastPID = millis();
  }
  
  checkSerialCommands();
}

void updateTemperatures() {
  sensors.requestTemperatures();
  double temp1 = sensors.getTempC(tempSensor1);
  double temp2 = sensors.getTempC(tempSensor2);
  Input = (temp1 + temp2) / 2.0;
}

void calculateFlow() {
  if (millis() - oldTime >= 1000) {
    detachInterrupt(digitalPinToInterrupt(FLOW_SENSOR));
    flowRate = (flowPulses * 2.25) / 70.0; // L/min para YF-S201
    flowPulses = 0;
    oldTime = millis();
    attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR), flowISR, FALLING);
  }
}

void computePID() {
  myPID.Compute();
}

void controlActuators() {
  // Control calentador/enfriador
  if (Output > 0) {
    analogWrite(HEATER_PIN, map(Output, 0, 100, 0, 255));
    analogWrite(COOLER_PIN, 0);
  } else {
    analogWrite(COOLER_PIN, map(abs(Output), 0, 100, 0, 255));
    analogWrite(HEATER_PIN, 0);
  }
}

void sendDataToSCADA() {
  Serial.print("<T1:");
  Serial.print(sensors.getTempC(tempSensor1));
  Serial.print(",T2:");
  Serial.print(sensors.getTempC(tempSensor2));
  Serial.print(",F:");
  Serial.print(flowRate);
  Serial.print(",H:");
  Serial.print((Output > 0) ? Output : 0);
  Serial.print(",C:");
  Serial.print((Output < 0) ? abs(Output) : 0);
  Serial.println(">");
}

void checkSerialCommands() {
  static String buffer;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      processCommand(buffer);
      buffer = "";
    } else {
      buffer += c;
    }
  }
}

void processCommand(String cmd) {
  if (cmd.startsWith("SETP:")) {
    Setpoint = cmd.substring(5).toFloat();
  }
  else if (cmd.startsWith("KP:")) {
    myPID.SetTunings(cmd.substring(3).toFloat(), myPID.GetKi(), myPID.GetKd());
  }
  else if (cmd.startsWith("KI:")) {
    myPID.SetTunings(myPID.GetKp(), cmd.substring(3).toFloat(), myPID.GetKd());
  }
  else if (cmd.startsWith("KD:")) {
    myPID.SetTunings(myPID.GetKp(), myPID.GetKi(), cmd.substring(3).toFloat());
  }
  else if (cmd == "EMSTOP") {
    digitalWrite(HEATER_PIN, 0);
    digitalWrite(COOLER_PIN, 0);
    digitalWrite(PUMP_PIN, 0);
  }
}
