#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <NTPClient.h>

#include <Arduino.h>
#include <cam_dev.h>

static bool status = false;
int ALARM_PIN = 21;

// WiFi credentials
const char* ssid = "WE DONT TALK ABOUT BRUNO";
const char* password = "umoi7006";

// MQTT server credentials
const char* mqttServer = "mqtt.eclipseprojects.io";
const int mqttPort = 1883;
const char* mqttTopic = "CN466/Alarm/house/myhouse";

// WiFi and MQTT clients
WiFiClient wifiClient;
WiFiClientSecure clientSecure;
PubSubClient mqttClient(wifiClient);

// NTP client setup
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000); // Update time every 60 seconds

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    connectToWiFi();
  }
}

void connectToMQTT() {
  Serial.print("Connecting to MQTT...");
  while (!mqttClient.connected()) {
    if (mqttClient.connect("ArduinoClient")) {
      Serial.println("connected");
    } else {
      Serial.print("failed with state ");
      Serial.println(mqttClient.state());
      delay(2000);
    }
  }
}

void send_image(uint8_t* buf, unsigned int buf_sz) {
    if (!mqttClient.connected()) {
        connectToMQTT();
    }

    // Update the NTP time
    timeClient.update();

    // Get the current time
    unsigned long epochTime = timeClient.getEpochTime();

    // Convert to a human-readable format
    char formattedTime[30];
    struct tm* timeInfo = gmtime((time_t*)&epochTime);
    snprintf(formattedTime, sizeof(formattedTime), "%02d-%02d-%04d %02d:%02d:%02d",
             timeInfo->tm_mday, timeInfo->tm_mon + 1, timeInfo->tm_year + 1900,
             timeInfo->tm_hour, timeInfo->tm_min, timeInfo->tm_sec);

    // Create the JSON message
    char message[150];
    snprintf(message, sizeof(message),
             "{\n"
             "  \"timestamp\": \"%s\",\n"
             "  \"image\": \"test.jpg\"\n"
             "}",
             formattedTime);

    mqttClient.publish(mqttTopic, message);

    Serial.print("Sending image by MQTT\n");
}

void setup() {
  Serial.begin(115200);

  pinMode(ALARM_PIN, INPUT);

  // Initialize camera
  status = cam_dev_init();
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup MQTT
  mqttClient.setServer(mqttServer, mqttPort);
  connectToMQTT();

  // Initialize NTP client
    timeClient.begin();
}

void loop() {
  // Ensure WiFi connection
  checkWiFiConnection();

  // Ensure the MQTT connection is active
  if (!mqttClient.connected()) {
    connectToMQTT();
  }
  mqttClient.loop();

  int alarmButton = digitalRead(ALARM_PIN);
  if (alarmButton) {
    static uint8_t buf[160 * 120 * 2] = {0};
    int buf_sz = cam_dev_snapshot(buf);
    if (buf_sz > 0) {
        send_image(buf, buf_sz);
    }
  }
}
