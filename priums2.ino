#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi i MQTT podešavanja
const char* ssid = "xs 2.4";
const char* password = "kzskjkmk7026";
const char* mqtt_server = "192.168.100.33"; // IP adresa tvog lokalnog MQTT brokera

WiFiClient espClient;
PubSubClient client(espClient);

// Definicije pinova
#define DHTPIN 14
#define DHTTYPE DHT11
#define FAN_PWM_PIN 26
#define RED_LED_PIN 13
#define WHITE_LED_PIN 12
#define SOIL_SENSOR_PIN 27
#define THRESHOLD 2800
#define BUZZER_PIN 25 // Dodao sam pin za buzzer

bool fanOn = true; // Promenljiva za praćenje stanja ventilatora

// Inicijalizacija DHT senzora
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(921600);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("Connected to WiFi");

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Inicijalizacija DHT senzora
  dht.begin();

  // Podešavanje PWM pina
  pinMode(FAN_PWM_PIN, OUTPUT);
  
  // Podešavanje LED pinova
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(WHITE_LED_PIN, OUTPUT);

  // Podešavanje buzzer pina
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("DHT11 i Ventilator kontrola");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Čitanje temperature i vlage
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Čitanje vrednosti senzora za vlažnost zemljišta
  int soilValue = analogRead(SOIL_SENSOR_PIN); // read the analog value from sensor
  float soilMoisturePercent = map(soilValue, 4095, 0, 0, 100); // map to percentage

  int fanSpeed = fanOn ? calculateFanSpeed(temperature) : 0; // Ako je ventilator isključen, brzina je 0
  analogWrite(FAN_PWM_PIN, fanSpeed);
  int fanSpeedPercentage = map(fanSpeed, 0, 255, 0, 100);

  // Priprema podataka za slanje
  String data = String("T:") + String(temperature, 2) + " H:" + String(humidity, 2) + " S:" + String(soilMoisturePercent, 2) + " F:" + String(fanSpeedPercentage);
  
  // Slanje podataka putem MQTT-a
  client.publish("sensor/data", data.c_str());
  
  // Ispisivanje podataka na serijskom portu
  Serial.print("Snaga ventilatora:");
  Serial.print(" (");
  Serial.print(fanSpeedPercentage);
  Serial.println("%)");
  
  if (soilValue > THRESHOLD)
    Serial.print("Suva zemlja! ");
  else
    Serial.print("Vlažna zemlja! ");
  
  Serial.print(soilMoisturePercent);
  Serial.println("%");

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Greška pri čitanju sa DHT senzora!");
    digitalWrite(RED_LED_PIN, HIGH);  // Upali crvenu LED
    digitalWrite(WHITE_LED_PIN, LOW); // Ugasi belu LED
  } else {
    digitalWrite(RED_LED_PIN, LOW);   // Ugasi crvenu LED
    digitalWrite(WHITE_LED_PIN, HIGH); // Upali belu LED

    Serial.println("====================");
    Serial.print("Vlažnost vazduha: ");
    Serial.print(humidity);
    Serial.print(" %\t");
    Serial.print("Temperatura: ");
    Serial.print(temperature);
    Serial.println(" *C");
  }
  
  Serial.println("====================");
  
  delay(3000);
}

// Funkcija za izračunavanje brzine ventilatora na osnovu temperature
int calculateFanSpeed(float temperature) {
  if (temperature >= 40) {
    return 255; // Maksimalna brzina
  } else if (temperature >= 35) {
    return 128; // 50% brzine
  } else if (temperature >= 32) {
    return 77; // 30% brzine
  } else {
    return 30; // Ventilator isključen
  }
}

void callback(char* topic, byte* message, unsigned int length) {
  String msg;
  for (int i = 0; i < length; i++) {
    msg += (char)message[i];
  }
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  Serial.println(msg);

  // Ako je primljena poruka "TOGGLE", aktiviraj/deaktiviraj sirenu
  if (String(topic) == "buzzer/control" && msg == "TOGGLE") {
    digitalWrite(BUZZER_PIN, !digitalRead(BUZZER_PIN));
  }

  // Ako je primljena poruka "TOGGLE", aktiviraj/deaktiviraj ventilator
  if (String(topic) == "fan/control" && msg == "TOGGLE") {
    fanOn = !fanOn;
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      client.subscribe("buzzer/control");
      client.subscribe("fan/control");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
