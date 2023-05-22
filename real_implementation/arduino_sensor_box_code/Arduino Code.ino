#include <SPI.h>
#include <SD.h>
#include <LoRa.h>
#include "ArduinoLowPower.h"
#include <MKRWAN.h>
#include <math.h>
#include <DFRobot_B_LUX_V30B.h>
#include <DFRobot_SHT3x.h>

LoRaModem modem;

String appEui;
String appKey;
String devAddr;
String nwkSKey;
String appSKey;

DFRobot_B_LUX_V30B myLux(/*address=*/0x94);//The sensor chip is set to 13 pins, SCL and SDA adopt default configuration
DFRobot_SHT3x sht3x(&Wire,/*address=*/0x44,/*RST=*/4);

#define Temp_Pos 0 // Set Digital pin 0 (HIGH, 3.3 V, temp pin power)
#define Temp_GND 1 // Set Digital pin 1 (LOW, 0 V, temp pin power)
#define Temp_Read A0  // Read temp sensor.

#define Moist1_Pos 2 // Set Digital pin 2 (HIGH, 3.3 V, temp pin power)
#define Moist1_GND 3 // Set Digital pin 3 (LOW, 0 V, temp pin power)
#define Moist1_Read A1 // Read the sensor voltage, determine resistance and lookup moisutre value.

#define Moist2_Pos 4 // Set Digital pin 2 (HIGH, 3.3 V, temp pin power)
#define Moist2_GND 5 // Set Digital pin 3 (LOW, 0 V, temp pin power)
#define Moist2_Read A2 // Read the sensor voltage, determine resistance and lookup moisutre value.

#define Moist_Read_Delay 0.1 // number of milliseconds in which the sensor must be read.

#define RE_DE 6 // Set Digital pin 6 to RE and DE for MAX3845 IC.
#define Q_PNPK A3 // Transistor Activate.

#define Q_TH A4 // Transistor Activate.
#define Q_Light A4 // Transistor Activate.

#define Q_BAT A5 // Transistor Activate.

#define Q_SD A4 // Transistor Activate.

#define CS_SD 7 // Chip Select for SD card pin 7.

float SenVTempC=0, SenVWM1=0, SenVWM2=0, ARead_A1=0, ARead_A2=0;
float  Calib_Resistance = 1;
float WM1_Resistance, WM2_Resistance, Acc_Lux, Amb_Lux,Bat_Read, Battery, Res_Check, Soil_Temp, Temp, Soil_T;

short int i, j, Sample, WM1_CB, WM2_CB, WM_CB, counter = 0;

float SupplyV = 3.3, Read_Delay;// Read_Delay;
float WM1_R_Offset = 1815.66; // Read 2365.66 ohms in water, so deviation by 1815.66. (550 ohms for 0 CB)
float WM2_R_Offset = 878.71; // Read 1428.71 ohms in water, so deviation by 1815.66. (550 ohms for 0 CB)

const short int Rx = 7870;  //fixed resistor attached in series to the sensor and ground...the same value repeated for all WM and Temp Sensor.
const short int default_TempC=24;
const int open_resistance=35000; //check the open resistance value by replacing sensor with an open and replace the value here...this value might vary slightly with circuit components 
const short int short_resistance=200; // similarly check short resistance by shorting the sensor terminals and replace the value here.
const short int short_CB=240, open_CB=255 ;
//const long TempC=24; 

float Amb_Temp_C, Amb_Temp_F, Amb_Humid, Acc_Temp_C, Acc_Temp_F, Acc_Humid;

short int connected, err;

short int nitro = 0;
short int phos = 0;
short int pot = 0;

float nitro_avg;
float phos_avg; 
float pot_avg;
float nitro_acc;
float phos_acc;
float pot_acc;

const byte npk_code[] = {0x01, 0x03, 0x00, 0x1e, 0x00, 0x03, 0x65, 0xCD}; // Address 1 Obtained from Modbus Program.
const byte ph_code[] = {0x02, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x38};; // Address2, high precision 0006

float ph_acc;
float ph_avg;

float pH_USE;

float NIT;
float PHOS;
float POT;

short int MAX3485_Time = 1000; //1000
short int set_delay = 1000; //1000


String num, filename = "";
String myData;



void setup() {  
  Serial.begin(9600);
  Serial1.begin(9600);
  analogReadResolution(12); 
  delay(10);

  pinMode(Temp_Pos, OUTPUT);
  pinMode(Temp_GND, OUTPUT);
  pinMode(Moist1_Pos, OUTPUT);
  pinMode(Moist1_GND, OUTPUT);
  pinMode(Moist2_Pos, OUTPUT);
  pinMode(Moist2_GND, OUTPUT);
  pinMode(RE_DE, OUTPUT); // Declare pin 6 (RE & DE) as an output.
  pinMode(Q_PNPK, OUTPUT);
  pinMode(Q_Light, OUTPUT);
  pinMode(Q_TH, OUTPUT);
  pinMode(Q_BAT, OUTPUT);
  pinMode(Q_SD, OUTPUT);
  pinMode(CS_SD, OUTPUT); // CHIP SELECT

  digitalWrite(Temp_Pos, LOW); // need high for timer circuit.
    
  digitalWrite(Temp_GND, LOW);
  digitalWrite(Moist1_Pos, LOW);
  digitalWrite(Moist1_GND, LOW);
  digitalWrite(Moist2_Pos, LOW);
  digitalWrite(Moist2_GND, LOW);
  digitalWrite(Moist2_GND, LOW);
  digitalWrite(CS_SD, LOW);


  enablePower(Q_PNPK, false);
  enablePower(Q_Light, false);
  enablePower(Q_TH, false);
  enablePower(Q_BAT, false);
  enablePower(Q_SD, false);
  
  if (!modem.begin(EU868)) {
  Serial.println("Failed to start module");
}

appEui = "0000000000000000";
appKey = "c1f1563eaa48956c962b60324c03f68a";

appKey.trim();
appEui.trim();

unsigned long start_time = millis(); // record the start time
while (!modem.joinOTAA(appEui, appKey)) {
  if (millis() - start_time > 2000) {    
    break; // exit the loop after 2 seconds
  }
  delay(1000); // wait for 1 second before trying again
}

  int err;
  modem.setPort(3);   
 
  }



void loop() {  

  digitalWrite(Temp_Pos, HIGH);
  digitalWrite(Temp_GND, LOW);  
  delay(100);  
  Soil_Temp = Soil_Temp_Sensor(3);      
  digitalWrite(Temp_Pos, LOW);
  // This function could be done with
  // being a function for one sensor,
  // not both together, would save power,
  // one being on whilst not being read.
  digitalWrite(Moist1_Pos, HIGH);
  digitalWrite(Moist2_Pos, HIGH);
  delay(100);
  Soil_Moist_Sensors(3, Soil_Temp);   
  digitalWrite(Moist1_Pos, LOW);
  enablePower(Moist2_Pos, LOW); 
  
  enablePower(Q_PNPK, true);
  delay(100);
  pH_Sensor(ph_code[8], 3);  
  
  delay(100);
  NPK_Sensor(npk_code[11], 3);  
  enablePower(Q_PNPK, false);

  enableI2C(true);
  enablePower(Q_Light, true);
  delay(100);
  Amb_Light(3);
  enableI2C(false);
  enablePower(Q_Light, false);

  enableI2C(true);
  enablePower(Q_TH, true);  
  delay(100);
  sht3x.begin();
  Amb_Temp_C = sht3x.getTemperatureC();
  Amb_Humid = sht3x.getHumidityRH();
  
  enableI2C(false);
  enablePower(Q_TH, false); 
  delay(100);

  enablePower(Q_BAT, false);
  delay(100);
  BAT_STAT(3);
  enablePower(Q_BAT,false);
  
  int temp = numpad(Soil_Temp);
  short int moist1 = abs(WM1_CB);
  short int moist2 = abs(WM2_CB);
  int my_pH = phnpk_bat_pad(pH_USE);
  int my_NIT = phnpk_bat_pad(NIT);
  int my_PHOS = phnpk_bat_pad(PHOS);
  int my_POT = phnpk_bat_pad(POT);
  int my_LUX = lux_pad(Amb_Lux);
  int my_Amb_Temp = numpad(Amb_Temp_C);
  int my_Amb_Humid = humpad(Amb_Humid);
  
  
  int my_Bat = phnpk_bat_pad(Battery);  

  byte value_bytes[28]; // Increase the size of the array by 2 to add in one byte for 255 and two bytes for pH
  memcpy(value_bytes, &temp, 4);
  memcpy(value_bytes + 4, &moist1, 1);
  memcpy(value_bytes + 5, &moist2, 1);
  memcpy(value_bytes + 6, &my_pH, 2);
  memcpy(value_bytes + 8, &my_NIT, 2);
  memcpy(value_bytes + 10, &my_POT, 2);
  memcpy(value_bytes + 12, &my_PHOS, 2);
  memcpy(value_bytes + 14, &my_LUX, 4);
  memcpy(value_bytes + 18, &my_Amb_Temp, 4);
  memcpy(value_bytes + 22, &my_Amb_Humid, 4);
  memcpy(value_bytes + 26, &my_Bat,2);  

  if (modem.connected()) {  
  modem.beginPacket();
  modem.write(value_bytes, sizeof(value_bytes)); // send byte array
  modem.endPacket(true);
  //err = modem.endPacket(true);
  delay(2000);   
  }
  
  counter++;

  enablePower(Q_SD,true);
  delay(100);    
  SD_Card();   
  enablePower(Q_SD,false);

  digitalWrite(Temp_GND, HIGH); 
  Serial.flush();
  modem.flush();
  Serial1.flush();

}


double Soil_Temp_Sensor(int samples){
  Soil_Temp = 0;
  //the samples initialized above, controls
  // the number of read successive read loops that is averaged.
  for (i=0; i<samples; i++)
  {
    
  delay(0.1); //wait 90 micro seconds and take sensor read was 0.09
  Soil_Temp += analogRead(Temp_Read); // read the temp sensor analog pin
  }

  SenVTempC=((Soil_Temp/4096)*SupplyV)/ samples;
  double TempC_Resistance = (Rx*(SupplyV-SenVTempC)/SenVTempC)*Calib_Resistance;
  double TempC=(-23.89*(log(TempC_Resistance)))+246.00;
  double Fitted_Temp = (0.84082*TempC)+(0.00235*(TempC*TempC))+ 1.69337;
  
  if (TempC_Resistance<0)
  {    
  TempC=default_TempC;
  }

  return Fitted_Temp;
}

void Soil_Moist_Sensors(int samples, double Temp){
  
  ARead_A1 = 0;   
  SenVWM1=0;
  ARead_A2 = 0;   
  SenVWM2=0;
  SenVTempC=0;

  Read_Delay = Moist_Read_Delay/samples;  
   //the samples initialized above,
   // controls the number of read successive
   // read loops that is averaged.
  for (i=0; i<samples; i++)
  {  
  delay(Read_Delay);  
  ARead_A1+=analogRead(Moist1_Read);     
  }
  //the samples initialized above, controls the
  // number of read successive read loops that is averaged.
  for (i=0; i<samples; i++)
  {
  delay(Read_Delay);  
  ARead_A2+=analogRead(Moist2_Read);
  }

  SenVWM1=((ARead_A1/4096)*SupplyV) / (samples); //get the average of the readings in the first direction and convert to volts  
  WM1_Resistance = (Rx*(SupplyV-SenVWM1)/SenVWM1) - WM1_R_Offset; //do the voltage divider math, using the Rx variable representing the known resistor

  SenVWM2=((ARead_A2/4096)*SupplyV) / (samples); //get the average of the readings in the first direction and convert to volts  
  WM2_Resistance = (Rx*(SupplyV-SenVWM2)/SenVWM2) - WM2_R_Offset; //do the voltage divider math, using the Rx variable representing the known resistor  

  WM1_CB = WM_CB_Value(WM1_Resistance);
  WM2_CB = WM_CB_Value(WM2_Resistance);

  ARead_A1 = 0;   
  SenVWM1=0;
  ARead_A2 = 0;   
  SenVWM2=0;
  SenVTempC=0;
}

int WM_CB_Value(double WM_Resistance){
  if (WM_Resistance>550.00) {
    
    if (WM_Resistance>8000.00) {      
      WM_CB=-2.246-5.239*(WM_Resistance/1000.00)*(1+.018*(Temp-24.00))-.06756*(WM_Resistance/1000.00)*(WM_Resistance/1000.00)*((1.00+0.018*(Temp-24.00))*(1.00+0.018*(Temp-24.00)));      
      
    } else if (WM_Resistance>1000.00) {
      WM_CB=(-3.213*(WM_Resistance/1000.00)-4.093)/(1-0.009733*(WM_Resistance/1000.00)-0.01205*(Temp)) ;

    } else {
      WM_CB=((WM_Resistance/1000.00)*23.156-12.736)*(1.00+0.018*(Temp-24.00));      
    }
    
  } else {
    if(WM_Resistance>300.00)  {
      WM_CB=0.00;      
    }
    
    if(WM_Resistance<300.00 && WM_Resistance>=short_resistance) {
      
      WM_CB=short_CB; //240 is a fault code for sensor terminal short      
    }
  }
  
  if(WM_Resistance>=open_resistance) {
    
    WM_CB=open_CB; //255 is a fault code for open circuit or sensor not present     
  }

  return WM_CB;
}

void Amb_Temp_Humid(int samples){     
  Amb_Temp_C, Amb_Temp_F, Amb_Humid, Acc_Temp_C, Acc_Temp_F, Acc_Humid = 0;
   
  sht3x.begin();
  
  Acc_Temp_C += sht3x.getTemperatureC();
  Acc_Temp_F += sht3x.getTemperatureF();
  Acc_Humid += sht3x.getHumidityRH();
    
  Amb_Temp_C = Acc_Temp_C;
  Amb_Temp_F = Acc_Temp_F;
  Amb_Humid = Acc_Humid; 

  Acc_Temp_C, Acc_Temp_F, Acc_Humid = 0;
  
  }



inline void enablePower(uint8_t Pin, bool enable)
{ 
  digitalWrite(Pin, enable ? LOW : HIGH); 
}

void enableI2C(bool enable){
  if (enable == true){
    // Return the SCL pin back to GPIO
    PORT->Group[g_APinDescription[SCL].ulPort].PINCFG[g_APinDescription[SCL].ulPin].bit.PMUXEN = 0;
  
    // Return the SDA pin back to GPIO
    PORT->Group[g_APinDescription[SDA].ulPort].PINCFG[g_APinDescription[SDA].ulPin].bit.PMUXEN = 0;
  }
  else
  {
    pinMode(SDA, OUTPUT);
    digitalWrite(SDA, HIGH);
    pinMode(SCL, OUTPUT);
    digitalWrite(SCL, HIGH);
  }
} 

void Amb_Light(int samples){     
  Amb_Lux = 0;  
  Acc_Lux = 0;
  
  delay(500);   
  myLux.begin();

  for (i=0; i<samples; i++){
    Acc_Lux += myLux.lightStrengthLux();        
    }  
  
  Amb_Lux = Acc_Lux/samples;    
  
  
  }

void BAT_STAT(int samples){
  Bat_Read = 0;
  Battery = 0;
  Res_Check = 0;

  for (i=0; i<samples; i++){    
    Res_Check = analogRead(A6);
    Bat_Read += analogRead(A6);   // read the battery from A6, samples times and add each time.    
  }
  Battery = 2*(((Res_Check  / 4096)*3.30));
  Bat_Read = 0; 
}

void SD_Card() {
  const char fixed_filename[12] = "File.txt";    

  // Step 1: Initialize the SD card
  if (!SD.begin(CS_SD)) {    
    return;
  }

  // Step 2: Open the fixed file with append mode (to avoid overwriting)
  File myFile = SD.open(fixed_filename, FILE_WRITE);

  if (myFile) {    
    myFile.print("Soil Temp (deg C): ");
    myFile.println(Soil_Temp);
    myFile.print("Soil Moisture 1 (CB): ");
    myFile.println(WM1_CB);
    myFile.print("Soil Moisture 2 (CB): ");
    myFile.println(WM2_CB);
    myFile.print("pH: ");
    myFile.println(pH_USE);
    myFile.print("Nitrogen (mg/kg): ");
    myFile.println(NIT);  
    myFile.print("Phosphorus (mg/kg): ");
    myFile.println(PHOS); 
    myFile.print("Potassium (mg/kg): ");
    myFile.println(POT);  
    myFile.print("Ambient Light (Lux): ");
    myFile.println(Amb_Lux);  
    myFile.print("Ambient Temp (deg C): ");
    myFile.println(Amb_Temp_C);  
    myFile.print("Ambient Humidity (%): ");
	myFile.println(Amb_Humid);
	myFile.print("Battery Voltage (V): ");
	myFile.println(Battery);
	myFile.println();
	myFile.close();
	} else {
	Serial.println("error opening " + String(fixed_filename));
	}
}

void pH_Sensor(const byte pH_request, int samples){  

  delay(100); // Need this delay to initialise the MAX3485.

  float ph_acc = 0;
  float ph_avg = 0;

  for (i=0; i<samples; i++){    
    if (Serial1.available() == 0) {
    digitalWrite(RE_DE, HIGH); // Set RE & DE, HIGH (to enable a transmit request from Arduino).
       
    
    Serial1.write(ph_code, sizeof(ph_code)); // Send the transmit request fram to the sensor.
    Serial1.flush(); // Wait for transmission of outgoing serial data to complete.
    digitalWrite(RE_DE, LOW); // Set RE & DE, HIGH (to enable a transmit request from Arduino).
    
  }
  
  delay(1000); // This is how long to wait for a response.
 
  byte ph_buffer[7]; // There are 7 bytes in the response.  (See Modbus response frame).


  if (Serial1.available() >= 7) { // If there is a response with at least 11 bytes of information then proceed.
    Serial1.readBytes(ph_buffer, 7); // Read in 11 bytes.
    // bytes 0-2 (three bytes) are ignored as these are the sensor address [0], function npk_code [1] and data length [2] respectively.
    float pH = ph_buffer[3] << 8 | ph_buffer[4]; // Do a bitwise operation, read the fourth byte [3], shift it by 8 bits and join the fifth byte[4] to it.   

    ph_acc += pH;

   }
    }

  
  ph_avg = ph_acc / samples;  
  pH_USE = ph_avg/100;  
  }


void NPK_Sensor(const byte npk_request, int samples){ 
  
  delay(100); // Need this delay to initialise the MAX3485.


  float nitro_acc = 0;
  float phos_acc = 0;
  float pot_acc = 0;

  float nitro_avg = 0;
  float phos_avg = 0;
  float pot_avg = 0;
   
  
  for (i=0; i<samples; i++){    
    if (Serial1.available() == 0) {
    digitalWrite(RE_DE, HIGH); // Set RE & DE, HIGH (to enable a transmit request from Arduino).
       
    
    Serial1.write(npk_code, sizeof(npk_code)); // Send the transmit request fram to the sensor.
    Serial1.flush(); // Wait for transmission of outgoing serial data to complete.
    digitalWrite(RE_DE, LOW); // Set RE & DE, HIGH (to enable a transmit request from Arduino).
    
  }

  delay(1000); // Setting Response Time for the Sensor.
 
  byte buffer[11]; // There are 11 bytes in the response.  (See Modbus response frame).


  if (Serial1.available() >= 11) { // If there is a response with at least 11 bytes of information then proceed.
    Serial1.readBytes(buffer, 11); // Read in 11 bytes.
    // bytes 0-2 (three bytes) are ignored as these are the sensor address [0], function npk_code [1] and data length [2] respectively.
    uint16_t nitro = buffer[3] << 8 | buffer[4]; // Do a bitwise operation, read the fourth byte [3], shift it by 8 bits and join the fifth byte[4] to it.
    uint16_t phos = buffer[5] << 8 | buffer[6]; // Do a bitwise operation, read the sixth byte [5], shift it by 8 bits and join the seventh byte [6] to it.
    uint16_t pot = buffer[7] << 8 | buffer[8]; // Do a bitwise operation, read the eigth byte [7], shift it by 8 bits and join the ninth byte [8] to it.
    // Thats because the response is 16-bit or two bytes so the second byte needs to be joined (bitwise) onto the first byte.
    
    // bytes 9 and 10 are ignored as these are the CRC_L and CRC_H.

    nitro_acc += nitro;
    phos_acc += phos;
    pot_acc += pot;

   }

    }
    

  nitro_avg = nitro_acc / samples;
  phos_avg = phos_acc / samples;
  pot_avg = pot_acc / samples;

  NIT = nitro_avg;
  PHOS = phos_avg;
  POT = pot_avg;
  }

  int numpad(float num) {
  String formatted_num = String(num, 2); // convert float to string with 2 decimal places
  if (formatted_num.indexOf('-') != -1) { // check if '-' exists in the string
    formatted_num.replace("-", ""); // remove '-'
    int int_num = static_cast<int>(formatted_num.toFloat() * 100 + 900000); // convert to float, multiply by 100, add 900000 and cast to int
    return int_num;
  }
  else {
    int int_num = static_cast<int>(formatted_num.toFloat() * 100 + 100000); // convert to float, multiply by 100, add 100000 and cast to int
    return int_num;
  }
}

int phnpk_bat_pad(float num) {  
  String formatted_num = String(num, 2); // convert float to string with 2 decimal places  
  int int_num = static_cast<int>(formatted_num.toFloat() * 100 + 10000); // convert to float, multiply by 100, add 10000 and cast to int  
  return int_num;
}

int lux_pad(float num) {
  int int_num = static_cast<int>(num * 100); // convert to float, multiply by 100 and cast to int
  int_num += 100000000; // add 100000000
  return int_num;
}

int humpad(float num) {
  Serial.print("Inside func Humid");
  Serial.println(num);
  String formatted_num = String(num, 2); // convert float to string with 2 decimal places  
  Serial.print("Formatted: ");
  Serial.println(formatted_num);
  int int_num = static_cast<int>(formatted_num.toFloat() * 100 + 10000); // convert to float, multiply by 100, add 100000 and cast to int
  Serial.print("Final Humid: ");
  Serial.println(int_num);
  return int_num;
  }