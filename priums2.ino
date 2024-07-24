#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <WiFi.h>

const char* ssid = "xs 2.4";
const char* password = "kzskjkmk7026";
const int port = 12345; // Port to listen on

WiFiServer server(port);

// Definicije pinova
#define DHTPIN 14
#define DHTTYPE DHT11
#define FAN_PWM_PIN 26
#define RED_LED_PIN 13
#define WHITE_LED_PIN 12
#define SOIL_SENSOR_PIN 27
#define THRESHOLD 2800

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
  server.begin();

  // Inicijalizacija DHT senzora
  dht.begin();

  // Podešavanje PWM pina
  pinMode(FAN_PWM_PIN, OUTPUT);
  
  // Podešavanje LED pinova
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(WHITE_LED_PIN, OUTPUT);

  Serial.println("DHT11 i Ventilator kontrola");
}

void loop() {
  // Čitanje temperature i vlage
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Čitanje vrednosti senzora za vlažnost zemljišta
  int soilValue = analogRead(SOIL_SENSOR_PIN); // read the analog value from sensor
  float soilMoisturePercent = map(soilValue, 4095, 0, 0, 100); // map to percentage
      
  int fanSpeed = calculateFanSpeed(temperature);
  analogWrite(FAN_PWM_PIN, fanSpeed);
  int fanSpeedPercentage = map(fanSpeed, 0, 255, 0, 100);

  // Priprema podataka za slanje
  String data = String("T:") + String(temperature, 2) + " H:" + String(humidity, 2) + " S:" + String(soilMoisturePercent, 2) + " F:" + String(fanSpeedPercentage);
  
  // Slanje podataka svim povezanim klijentima
  WiFiClient client = server.available();
  if (client) {
    client.println(data);
  }
  
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
