#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include "credentials.h"

// WiFi credentials and UDP setup
// taken from  credentials.h

WiFiUDP udp;
unsigned int localUdpPort = 4210; // local port to listen on
char incomingPacket[255];         // buffer for incoming packets
unsigned long lastPacketTime = 0; // Time when the last packet was received

// Motor control pins

 
#ifdef TTGO_T18
const int leftMotorForward = 25;
const int leftMotorBackward = 33;
const int rightMotorForward = 27;
const int rightMotorBackward = 26;
#endif

#ifdef SEEED_XIAO_ESP32S3
const int leftMotorForward = D0;
const int leftMotorBackward = D1;
const int rightMotorForward = D2;
const int rightMotorBackward = D3;
#endif



//#define UDPDEBUG

 
#ifdef  UDPDEBUG
 
WiFiUDP debugUdp;
const char* debugIp = "192.168.0.218"; // IP of your computer
const unsigned int debugPort = 4211;  // Port on which to receive debug messages

void debugPrint(String message) {
  debugUdp.beginPacket(debugIp, debugPort);
  debugUdp.write((const uint8_t*)message.c_str(), message.length());
  debugUdp.endPacket();
}
 
 #endif

const char* currentSSID;
const char* currentPassword;

void chooseNetwork() {
  WiFi.mode(WIFI_STA);
  WiFi.setHostname("Enterprise");

  int n = WiFi.scanNetworks();
  bool primaryFound = false;
  bool secondaryFound = false;

  for (int i = 0; i < n; ++i) {
    String ssid = WiFi.SSID(i);
    if (ssid == primarySSID) {
      primaryFound = true;
    }
    if (ssid == secondarySSID) {
      secondaryFound = true;
    }
  }

  if (primaryFound) {
    currentSSID = primarySSID;
    currentPassword = primaryPassword;
  } else if (secondaryFound) {
    currentSSID = secondarySSID;
    currentPassword = secondaryPassword;
  } else {
    currentSSID = secondarySSID; // Default to secondary if neither is found
    currentPassword = secondaryPassword;
  }

  Serial.printf("Selected network: %s\n", currentSSID);
  Serial.printf("SSID length: %d\n", strlen(currentSSID));
  Serial.printf("Password length: %d\n", strlen(currentPassword));
}

void setupWiFi() {
  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(currentSSID, currentPassword);
    Serial.printf("Connecting to %s", currentSSID);
    bool connected = false;
    for (int i = 0; i < 20; i++) { // Try for 5 seconds
      if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\nConnected to %s\n", currentSSID);
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        connected = true;
        break;
      }
      delay(250);
      Serial.print(".");
    }

    if (connected) {
      break;
    }

    Serial.printf("\nFailed to connect to %s\n", currentSSID);
    delay(250); // Wait before retrying
  }
}

void setup()
{
  Serial.begin(115200);
  pinMode(leftMotorForward, OUTPUT);
  pinMode(leftMotorBackward, OUTPUT);
  pinMode(rightMotorForward, OUTPUT);
  pinMode(rightMotorBackward, OUTPUT);

  chooseNetwork();
  setupWiFi();
  udp.begin(localUdpPort);
  Serial.printf("UDP server started at %s:%u\n", WiFi.localIP().toString().c_str(), localUdpPort);
  ArduinoOTA.begin(); // Initialize OTA
}

void controlMotor(int pinForward, int pinBackward, int speed)
{
 
 

  if (speed > 0)
  {
    analogWrite(pinBackward, 0);
    analogWrite(pinForward, speed);
    
    
    
  }
  else if (speed < 0)
  {
    analogWrite(pinForward, 0);
    analogWrite(pinBackward, -speed);
  }
  else
  {
    analogWrite(pinForward, 0);
    analogWrite(pinBackward, 0);
  }
}

void panic()
{
  controlMotor(leftMotorForward, leftMotorBackward, 0);
  controlMotor(rightMotorForward, rightMotorBackward, 0);


  Serial.print("."); // Motors stopped due to no UDP packet received for 1 second.");
}

void handleMotorControl(char *packet)
{
  int leftSpeed, rightSpeed;
  sscanf(packet, "%d %d", &leftSpeed, &rightSpeed); // Parse speeds for both motors
  #ifdef  UDPDEBUG
  debugPrint(String(leftSpeed) + " "  +  String(rightSpeed));
  #endif
  controlMotor(leftMotorForward, leftMotorBackward, leftSpeed);
  controlMotor(rightMotorForward, rightMotorBackward, rightSpeed);

}

void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    setupWiFi(); // Reconnect to WiFi if disconnected
  }

  int packetSize = udp.parsePacket();

  if (packetSize == 0)
  {
   


    unsigned long currentMillis = millis();
    if (currentMillis - lastPacketTime >= 500)
        {          // More than 0.5 second since last packet
          lastPacketTime=currentMillis;  // to evade endless panic messages spam that  affects ping mesurement on
          panic(); // Stop the motors
          delay(10); // dark magic here. If there is no delay, panic stop does not work, looks like analogwrite does not keep up.
        
          #ifdef  UDPDEBUG
          debugPrint("ZERO UDP PACKAGES TIMEOUT\n");
          #endif
        }
  }


  if (packetSize > 0)
  {
    int len = udp.read(incomingPacket, 254); // Read up to 254 bytes
    if (len > 0)
    {
      incomingPacket[len] = 0; // Null-terminate the string
      //debugPrint("Received Packet: " + String(incomingPacket)); // Send incoming packet to debug output
    //Serial.print("Received Packet: " + String(incomingPacket)); // Send incoming packet to debug output
  
      handleMotorControl(incomingPacket);
      lastPacketTime = millis(); // Update the time of the last received packet
    }
  }
   

  ArduinoOTA.handle();
}


 


