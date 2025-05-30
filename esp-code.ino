#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

// WiFi credentials - UPDATE THESE
const char* ssid = "samsung50";        // Replace with your WiFi name
const char* password = "abcd1234"; // Replace with your WiFi password

// HiveMQ Cloud settings
const char* mqtt_server = "6da50eee270d490d86688a1ad70aa6dc.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "AgroSphere";          // Your HiveMQ username
const char* mqtt_password = "AgroSpherex3421";  // Your HiveMQ password

// Device settings - UPDATED WITH YOUR INFO
const char* device_owner = "pasindu";       // Your username in the web app
const char* device_id = "1122334455";       // The device ID you entered
const char* device_name = "green";          // The device name you entered

// Pin configuration
const int ledPin = 15;       // Built-in LED (GPIO2)
const int sensorPin = 16;   // Analog input pin (GPIO34)

WiFiClientSecure espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
float lastSensorValue = 0;
bool ledState = false;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  String topicStr = String(topic);
  
  if (topicStr.endsWith("led/control")) {
    if (message == "ON") {
      digitalWrite(ledPin, HIGH);
      ledState = true;
      Serial.println("LED turned ON");
      publishLedStatus();
    } else if (message == "OFF") {
      digitalWrite(ledPin, LOW);
      ledState = false;
      Serial.println("LED turned OFF");
      publishLedStatus();
    }
  }
}

void publishLedStatus() {
  String topic = String("greenhouse/") + device_owner + "/" + device_id + "/led/status";
  if (client.publish(topic.c_str(), ledState ? "ON" : "OFF")) {
    Serial.println("LED status published");
  } else {
    Serial.println("Failed to publish LED status");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      
      String subscribeTopic = String("greenhouse/") + device_owner + "/" + device_id + "/led/control";
      if (client.subscribe(subscribeTopic.c_str())) {
        Serial.println("Subscribed to control topic");
      } else {
        Serial.println("Subscribe failed");
      }
      
      // Publish initial status
      publishLedStatus();
      
      // Publish device online status
      String onlineTopic = String("greenhouse/") + device_owner + "/" + device_id + "/status";
      client.publish(onlineTopic.c_str(), "online");
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);  // Start with LED off
  
  setup_wifi();
  
  // Configure TLS - using insecure for now to test (like your working example)
  espClient.setInsecure(); // Bypass certificate validation
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  client.setBufferSize(2048);  // Increase buffer size if needed
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  unsigned long now = millis();
  if (now - lastMsg > 2000) {  // Publish every 2 seconds
    lastMsg = now;
    
    // Read sensor
    int rawValue = analogRead(sensorPin);
    float sensorValue = rawValue * (3.3 / 4095.0);  // Convert to voltage
    
    // Only publish if value changed significantly (10% change or more)
    if (abs(sensorValue - lastSensorValue) >= (lastSensorValue * 0.10) || lastSensorValue == 0) {
      lastSensorValue = sensorValue;
      
      String topic = String("greenhouse/") + device_owner + "/" + device_id + "/sensor";
      String payload = String(rawValue);  // Send only raw ADC value
      
      if (client.publish(topic.c_str(), payload.c_str())) {
        Serial.print("Published sensor value: ");
        Serial.println(payload);
      } else {
        Serial.println("Failed to publish sensor value");
      }
    }
  }
}