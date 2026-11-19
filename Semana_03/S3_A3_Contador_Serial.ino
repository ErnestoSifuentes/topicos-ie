/* Semana 3 · A3. Conteo LOW->HIGH. Formato CSV: t_ms,ciclos,estado.
   GPIO23 -> R330 -> LED -> GND. 115200 baudios.
*/
#include <Arduino.h>
constexpr uint8_t LED_PIN = 23;
constexpr uint32_t T_HALF_MS = 250;
uint32_t previousMs = 0;
uint32_t cycles = 0;
bool state = false;
void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);
  Serial.println("t_ms,ciclos,estado");
  previousMs = millis();
}
void loop() {
  uint32_t now = millis();
  if ((uint32_t)(now - previousMs) >= T_HALF_MS) {
    previousMs = now;
    state = !state;
    digitalWrite(LED_PIN, state ? HIGH : LOW);
    if (state) ++cycles;
    Serial.print(now); Serial.print(',');
    Serial.print(cycles); Serial.print(','); Serial.println(state ? 1 : 0);
  }
}
