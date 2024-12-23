#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <PubSubClient.h>

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
const char* mqttTopic = "CN466/Alarm/myhouse";
const char* server = "https://lqmf0w3x-5002.asse.devtunnels.ms/"

char mqttCameraTopic[50];
char uploadPath[100];
char videoPath[100];

char* mqttCamera

// WiFi and MQTT clients
WiFiClient wifiClient;
WiFiClientSecure clientSecure;
PubSubClient mqttClient(wifiClient);


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

void captureAndUploadImage(const char* url) {
    if (image_buf == nullptr) {
        Serial.println("Image buffer is not allocated. Skipping capture.");
        return;
    }

    int image_size = cam_dev_snapshot(image_buf);
    if (image_size <= 0) {
        Serial.println("Failed to capture image or invalid image size.");
        return;
    }

    HTTPClient http;
    clientSecure.setCACert(certificate);
    http.begin(clientSecure, url);
    http.setTimeout(5000);

    String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
    String form_data_start = "--" + boundary + "\r\n" +
                             "Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n" +
                             "Content-Type: image/jpeg\r\n\r\n";
    String form_data_end = "\r\n--" + boundary + "--\r\n";

    int total_length = form_data_start.length() + image_size + form_data_end.length();
    char *body = (char*)malloc(total_length);
    if (body == nullptr) {
        Serial.println("Failed to allocate memory for HTTP body.");
        return;
    }

    memcpy(body, form_data_start.c_str(), form_data_start.length());
    memcpy(body + form_data_start.length(), image_buf, image_size);
    memcpy(body + form_data_start.length() + image_size, form_data_end.c_str(), form_data_end.length());

    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    int httpResponseCode = http.POST((uint8_t*)body, total_length);

    if (httpResponseCode > 0) {
        Serial.print("Image upload successful, HTTP response code: ");
        Serial.println(httpResponseCode);
        String response = http.getString();
        Serial.print("Response message: ");
        Serial.println(response);
    } else {
        Serial.print("Error on image upload, code: ");
        Serial.println(httpResponseCode);
    }

    free(body);
    http.end();
}
}

void setup() {
  Serial.begin(115200);

  strcpy(mqttCameraTopic, bound);
  strcat(mqttCameraTopic, gate);

  pinMode(ALARM_PIN, INPUT);

  // Initialize camera
  status = cam_dev_init();
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup MQTT
  mqttClient.setServer(mqttServer, mqttPort );
  mqttClient.setCallback(mqttCallback);
  connectToMQTT();
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
    mqttClient.publish(mqttCameraTopic, "Alarm");
    captureAndUploadImage(videoPath);
  }
}
