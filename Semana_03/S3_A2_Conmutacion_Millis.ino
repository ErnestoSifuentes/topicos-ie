/* Semana 3 · A2. Temporizacion cooperativa sin delay().
   Misma conexion que en A1. Verifique T y THIGH con osciloscopio.
*/
#include <Arduino.h>
constexpr uint8_t LED_PIN = 23;
constexpr uint32_t T_HALF_MS = 125;
uint32_t previousMs = 0;
bool state = false;
void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  previousMs = millis();
}
void loop() {
  const uint32_t now = millis();
  if ((uint32_t)(now - previousMs) >= T_HALF_MS) {
    previousMs = now;
    state = !state;
    digitalWrite(LED_PIN, state ? HIGH : LOW);
  }
  // Pueden añadirse tareas de lectura sin detener el programa.
}
