#include <DHT.h>

constexpr uint8_t DHT_PIN = 4;
constexpr uint8_t DHT_TYPE = DHT11;
constexpr char DEVICE_ID[] = "esp32s3-01";
constexpr char FIRMWARE_VERSION[] = "1.0";
constexpr unsigned long SAMPLE_INTERVAL_MS = 2000;

DHT dht(DHT_PIN, DHT_TYPE);
unsigned long sequenceNumber = 0;
unsigned long lastSampleMs = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  const unsigned long now = millis();
  if (now - lastSampleMs < SAMPLE_INTERVAL_MS) {
    return;
  }

  lastSampleMs = now;
  ++sequenceNumber;

  const float humidity = dht.readHumidity();
  const float temperatureC = dht.readTemperature();

  if (isnan(humidity) || isnan(temperatureC)) {
    Serial.printf(
        "{\"device_id\":\"%s\",\"seq\":%lu,\"status\":\"sensor_error\","
        "\"firmware\":\"%s\"}\n",
        DEVICE_ID,
        static_cast<unsigned long>(sequenceNumber),
        FIRMWARE_VERSION);
    return;
  }

  Serial.printf(
      "{\"device_id\":\"%s\",\"seq\":%lu,\"status\":\"ok\","
      "\"temperature_c\":%.1f,\"humidity_percent\":%.1f,"
      "\"firmware\":\"%s\"}\n",
      DEVICE_ID,
      static_cast<unsigned long>(sequenceNumber),
      temperatureC,
      humidity,
      FIRMWARE_VERSION);
}
