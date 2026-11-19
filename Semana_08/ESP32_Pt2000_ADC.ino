// INTERFAZ-IA | ESP32 DOIT DevKit V1 | Practicas 2 y 3 | Pt2000
// Firmware comun: GPIO36 / ADC1_CH0, salida CSV limpia a 115200 bps.
// Se utiliza analogReadMilliVolts() (calibracion interna si esta disponible).
// Cada paquete: t_ms,adc_raw,adc_mV  (sin encabezados ni mensajes extra).
#include <Arduino.h>
constexpr int ADC_PIN = 36;
constexpr uint32_t SAMPLE_MS = 250;
uint32_t previousMs = 0;
void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(ADC_PIN, ADC_11db);
  pinMode(ADC_PIN, INPUT);
}
void loop() {
  uint32_t now = millis();
  if (now - previousMs >= SAMPLE_MS) {
    previousMs = now;
    uint16_t raw = analogRead(ADC_PIN);
    uint32_t mv = analogReadMilliVolts(ADC_PIN);
    Serial.print(now); Serial.print(',');
    Serial.print(raw); Serial.print(',');
    Serial.println(mv);
  }
}
