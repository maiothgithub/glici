//Glici in the Matrix ;-)
//© Olimpics
//2025
//Ver.3.4.5

//Libaries//
#include <WEMOS_SHT3X.h>//my temperature and humidity sensor
#include <ESP8266WiFi.h>//my 8266 WiFi

//Global declarations
SHT3X sht30(0x44); //adress of SHT30
const int analogInPin = A0;  //ADC-pin of AZ-Envy for the gas sensor
const int integrated_led = 2; //integrated led is connected to D2

//AP info
const char* ssid = "DOVA";
const char* password =  "fidobase";

//PC - python client
const char* host ="192.168.188.24";
const int port=8080;

WiFiClient client;

//variables to work with
float temperature;
float humidity;
int sensorValue;

//to calibrate temperature values
float temperature_deviation = 5.1;
float temperature_calibrated = temperature - temperature_deviation;


// Define a struct with the data we want to send
struct DataPacket {
  float temperature;
  float humidity;
  int32_t irSensor;
};

DataPacket packet;

void WiFiSetup()
{
  Serial.println("Connecting to WiFi..");
  delay(1000);

  // Connect to WiFi network
  Serial.println();
  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Connected to the WiFi network");
  Serial.println(WiFi.localIP());

}

void PrintValues()
{
  Serial.println("----------------------------------------------");
  Serial.print("Temperature in Celsius: ");
  Serial.println(temperature_calibrated);
  Serial.print("Relative Humidity: ");
  Serial.println(humidity);
  Serial.print("IRvalue:");
  Serial.println(sensorValue);
  Serial.println("----------------------------------------------");
}

void PrintSentData()
{
  // Convert float values to a simple string format
  String data = String(temperature_calibrated, 2) + "," + 
                String(humidity, 2) + "," + 
                String(sensorValue) + "\n";

  // Send data
  Serial.print("Sent: ");
  Serial.println(data);
}

void setup() 
{
  Serial.begin(115200); //starting the serial communication with a baud rate of 115200 bps
  Serial.println("------------------------------");
  Serial.println("-------------Glici------------");
  Serial.println("----------by Olimpics---------");
  Serial.println("------------------------------");

  pinMode(analogInPin, INPUT); //set ADC-pin as a input
  pinMode(integrated_led, OUTPUT); //set the integrated led as a output

  WiFiSetup();
}

void loop() 
{
  if (sht30.get() == 0) {
  
    temperature = sht30.cTemp;
    humidity = sht30.humidity;
    sensorValue = analogRead(analogInPin); //read the ADC-pin 
    temperature_calibrated = temperature - temperature_deviation;

    PrintValues();

    if (client.connect(host, port)) {
      packet.temperature = temperature_calibrated;
      packet.humidity = humidity;
      packet.irSensor = sensorValue;

      client.write((uint8_t*)&packet, sizeof(packet));
      PrintSentData();
      client.stop();  // Close connection after each send
    } else {
      Serial.println("Connection to server failed.");
    }
  }
  else //if useless values are measured
  {
    Serial.println("Error, please check hardware or code!");
  }

  //life sign to know the HW is still working
  digitalWrite(integrated_led, HIGH); //turn led on
  delay(500);
  digitalWrite(integrated_led, LOW); //turn led off

  delay(5000);  // Send every 5 seconds
}