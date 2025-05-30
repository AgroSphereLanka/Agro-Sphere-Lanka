#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

// WiFi credentials
const char* ssid = "samsung50";
const char* password = "abcd1234";

// HiveMQ Cloud settings
const char* mqtt_server = "6da50eee270d490d86688a1ad70aa6dc.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "AgroSphere";
const char* mqtt_password = "AgroSpherex3421";

// Device settings
const char* device_owner = "pasindu";
const char* device_id = "1122334455";
const char* device_name = "green";

// Pin configuration
const int ledPin = 15;       // LED pin
const int sensorPin = 16;     // Analog input pin

WiFiClientSecure espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
const long publishInterval = 1000; // 1 second interval

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
      Serial.println("LED turned ON");
      publishLedStatus();
    } else if (message == "OFF") {
      digitalWrite(ledPin, LOW);
      Serial.println("LED turned OFF");
      publishLedStatus();
    }
  }
}

void publishLedStatus() {
  String topic = String("greenhouse/") + device_owner + "/" + device_id + "/led/status";
  if (client.publish(topic.c_str(), digitalRead(ledPin) ? "ON" : "OFF")) {
    Serial.println("LED status published");
  } else {
    Serial.println("Failed to publish LED status");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      
      String subscribeTopic = String("greenhouse/") + device_owner + "/" + device_id + "/led/control";
      client.subscribe(subscribeTopic.c_str());
      
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
  
  // Configure TLS - using insecure for testing
  espClient.setInsecure();
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  client.setBufferSize(2048);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  unsigned long now = millis();
  if (now - lastMsg > publishInterval) {
    lastMsg = now;
    
    // Read and publish sensor value every second
    int rawValue = analogRead(sensorPin);
    String topic = String("greenhouse/") + device_owner + "/" + device_id + "/sensor";
    
    if (client.publish(topic.c_str(), String(rawValue).c_str())) {
      Serial.print("Published sensor value: ");
      Serial.println(rawValue);
    } else {
      Serial.println("Failed to publish sensor value");
    }
  }
}