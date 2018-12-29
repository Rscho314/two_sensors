
/*******************************************************************
 * 
 * This is a test for using both the BME680 & MAX31856 together
 * 
 *******************************************************************/
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_MAX31856.h>

#define SCK 13
#define MISO 12
#define MOSI 11
#define BME_CS 9
#define MAX_CS 10
#define SEA_LVL_P (1013.25)

Adafruit_BME680 bme(BME_CS, MOSI, MISO,  SCK);
Adafruit_MAX31856 maxthermo = Adafruit_MAX31856(MAX_CS, MOSI, MISO, SCK);

void setup() {
  digitalWrite(BME_CS, HIGH);
  digitalWrite(MAX_CS, HIGH);
  Serial.begin(115200);
  
  maxthermo.begin();
  maxthermo.setThermocoupleType(MAX31856_TCTYPE_T);

  bme.begin();
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms
  
}

void loop() {
  digitalWrite(BME_CS, LOW);
  bme.performReading();
  Serial.print("bme: ");
  Serial.print(bme.temperature); //°C
  Serial.print(" ");
  Serial.print(bme.pressure); //Pa
  Serial.print(" ");
  Serial.print(bme.humidity); //%
  Serial.print(" ");
  Serial.print(bme.gas_resistance); //Ohm
  Serial.print(" ");
  Serial.print(bme.readAltitude(SEA_LVL_P)); //m
  Serial.println("");
  digitalWrite(BME_CS, HIGH);

  digitalWrite(MAX_CS, LOW);
  Serial.print("max: ");
  Serial.print(maxthermo.readThermocoupleTemperature()); //°C
  Serial.print(" ");
  Serial.print(maxthermo.readCJTemperature()); //°C
  Serial.println("");
  digitalWrite(MAX_CS, HIGH);
  
  delay(750);
}
