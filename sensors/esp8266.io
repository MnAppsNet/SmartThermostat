#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP8266WiFi.h>

//Sensor
Adafruit_BME280 bmp280;

//Credentials
const char* ssid = "YOUR_SSID_HERE";
const char* password = "YOUR_PASSWORD_HERE";

// Set web server port number to 80
WiFiServer server(80);
// Variable to store the HTTP request
String header;

// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 0;
// Define timeout time in milliseconds (example: 2000ms = 2s)
const long timeoutTime = 10000;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  // Connect to Wi-Fi network with SSID and password
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Print local IP address and start web server
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();

  Wire.begin();
  bmp280.begin(0x76);
}

void loop(){
  WiFiClient client = server.available(); // Listen for incoming clients
  if (client) { // If a new client connects,
    Serial.println("New Client."); // print a message out in the serial port
    Serial.println(client.localIP());
    String currentLine = ""; // make a String to hold incoming data from the client
    currentTime = millis();
    previousTime = currentTime;
    while (client.connected() && currentTime - previousTime <= timeoutTime) { // loop while the client’s connected
      digitalWrite(LED_BUILTIN, LOW);
      currentTime = millis();
      if (client.available()) { // if there’s bytes to read from the client,
        char c = client.read(); // read a byte, then
        Serial.write(c);        // print it out the serial monitor
        header += c;
        if (c == 'n') { // if the byte is a newline character
        // if the current line is blank, you got two newline characters in a row.
        // that’s the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what’s coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:application/json");
            client.println("Connection: close");
            client.println();
            String pressure = String(bmp280.readPressure() * 0.000009869233F);
            String temperature = String(bmp280.readTemperature());
            String humidity = String(bmp280.readHumidity());
            // Display the HTML web page
            client.println("{\"temperature\":\""+temperature+"\",\"pressure\":\""+pressure+"\",\"humidity\":\""+humidity+"\"}");
            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
      } else if (c != 'r') {  // if you got anything else but a carriage return character,
        currentLine += c;      // add it to the end of the currentLine
      }
    }
  }
  // Clear the header variable
  header = "";
  }
  digitalWrite(LED_BUILTIN, HIGH);
}