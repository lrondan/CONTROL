/*  Inlcude file for _______ process trainer serial number _____
    In this file define only hardware addresses, and specific arduino ports to be used
*/
/* ############Don't change below this line###############*/
// First we include the libraries
#include <OneWire.h>            // communication protocol for OneWire devies
#include <DallasTemperature.h>  // Library for DS Temperature Sensor
//#include <LCD_I2C.h>            // Communication with liquid crystal display with I2C communications
//#include <LiquidCrystal.h>      // Communication with liquid crystal display withour I2C communication
#include "vcc_001_01.h"

OneWire oneWire(ONE_WIRE_BUS);  // Setup an instance to communicate with any 1-Wire devices  
DallasTemperature TEMP_SENS(&oneWire);

double TEMP_TT1 = 0;            // Temp TT1
double TEMP_TT2 = 0;            // Temp TT2
unsigned long StartTime;
unsigned int  BRANCH = 1;       // Start in branch 1 to force complete start cycle