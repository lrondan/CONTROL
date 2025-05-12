/*  Inlcude file for VSEN022 process trainer serial number 002
    In this file define only hardware addresses, and specific arduino ports to be used
    In this code the relays are working in low performance
*/
/* ############Don't change below this line###############*/
// First we include the libraries
#include <PID_v1.h>
#include <OneWire.h>            // communication protocol for OneWire devies
#include <DallasTemperature.h>  // Library for DS Temperature Sensor
#include <Wire.h>
#include <LiquidCrystal_I2C.h>// Communication with liquid crystal display withour I2C communication

DeviceAddress sensor1 = {0x28, 0x81, 0x8E, 0x53, 0x3A, 0x19, 0x01, 0x4E}; // Temp sensor in Heater tank
DeviceAddress sensor2 = {0x28, 0x32, 0xA0, 0x5B, 0x3A, 0x19, 0x01, 0x56}; // Temp sensor Outflow Heat Exchanger
OneWire oneWire(8);  // Setup an instance to communicate with any 1-Wire devices  
DallasTemperature sensors(&oneWire);

const byte FLOW_SENSOR  = 2;          // Flow sensor
const byte HEATER_TRIAC = 9;        // Heater is activated from Arduino UNO pin 9
const byte PUMP_PIN     = 5;          // Pump   is activated from Arduino UNO pin 5
const byte COOLER_PIN   = 6;          // Fan    is activared from Arduino UNO pin 6
volatile int ZeroCrossPin = 3;      // INT0, send intrps to triac
volatile bool zero_cross = false;   // flag down
int power = 50;                     // Level of heater (50%)
int delay_Time = 0;
double temp1 = 0;                   // Temp in Process Vessel
double temp2 = 0;                   // Temp after heat exchanger
unsigned long StartTime;

// PID Variables
double Setpoint = 40.0; // Default setpoint
double Input, Output;
double Kp=4.0, Ki=0.2, Kd=1.0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

// Flow sensor variables
volatile int pulseCount = 0;
float flowRate = 0.0;
unsigned long oldTime;

LiquidCrystal_I2C lcd(0x27, 20, 4);  // I2C (0x27 o 0x3F)

//Config for relays
#define ON  LOW
#define OFF HIGH