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
const int leftMotorForward = D0;
const int leftMotorBackward = D1;
const int rightMotorForward = D2;
const int rightMotorBackward = D3;

/*
WiFiUDP debugUdp;
const char* debugIp = "192.168.0.218"; // IP of your computer
const unsigned int debugPort = 4211;  // Port on which to receive debug messages

void debugPrint(String message) {
  debugUdp.beginPacket(debugIp, debugPort);
  debugUdp.write((const uint8_t*)message.c_str(), message.length());
  debugUdp.endPacket();
}
*/
void setupWiFi()
{
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup()
{
  Serial.begin(115200);
  pinMode(leftMotorForward, OUTPUT);
  pinMode(leftMotorBackward, OUTPUT);
  pinMode(rightMotorForward, OUTPUT);
  pinMode(rightMotorBackward, OUTPUT);

  setupWiFi();
  udp.begin(localUdpPort);
  Serial.printf("UDP server started at %s:%u\n", WiFi.localIP().toString().c_str(), localUdpPort);
  ArduinoOTA.begin(); // Initialize OTA
}

void controlMotor(int pinForward, int pinBackward, int speed)
{
  if (speed > 0)
  {
    analogWrite(pinForward, speed);
    analogWrite(pinBackward, 0);
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


  Serial.println("Panic: Motors stopped due to no UDP packet received for 1 second.");
}

void handleMotorControl(char *packet)
{
  int leftSpeed, rightSpeed;
  sscanf(packet, "%d %d", &leftSpeed, &rightSpeed); // Parse speeds for both motors
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
          panic(); // Stop the motors
          delay(10); // dark magic here. If there is no delay, panic stop does not work, looks like analogwrite does not keep up.
       //    debugPrint("ZERO UDP PACKAGES TIMEOUT\n");
        }
  }


  if (packetSize > 0)
  {
    int len = udp.read(incomingPacket, 254); // Read up to 254 bytes
    if (len > 0)
    {
      incomingPacket[len] = 0; // Null-terminate the string
      // debugPrint("Received Packet: " + String(incomingPacket)); // Send incoming packet to debug output
  
      handleMotorControl(incomingPacket);
      lastPacketTime = millis(); // Update the time of the last received packet
    }
  }
   

  ArduinoOTA.handle();
}


 


