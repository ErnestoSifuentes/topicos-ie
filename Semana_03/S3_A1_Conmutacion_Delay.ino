/* Semana 3 · A1. Periodo total T = 2*T_HALF_MS.
   DOIT ESP32 DevKit V1. GPIO23 -> R330 -> anodo LED; catodo -> GND.
   T_HALF_MS: 125,250,500,1000 -> 250,500,1000,2000 ms.
*/
#include <Arduino.h>
constexpr uint8_t LED_PIN = 23;
constexpr uint32_t T_HALF_MS = 125;  // Cambiar para cada experimento.
void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}
void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(T_HALF_MS);
  digitalWrite(LED_PIN, LOW);
  delay(T_HALF_MS);
}
