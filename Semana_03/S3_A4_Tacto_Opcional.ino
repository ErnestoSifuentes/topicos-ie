/* Reto opcional de la Leccion 3. SOLO ESP32 clasico con Touch GPIO4.
   Calibrar umbral midiendo primero valores libre/tocado en Monitor Serial.
   LED GPIO23 con resistencia de 330 ohmios a GND.
*/
#include <Arduino.h>
constexpr uint8_t TOUCH_GPIO = 4;
constexpr uint8_t LED_PIN = 23;
uint16_t threshold = 25;   // EJEMPLO: ajustar con lecturas reales
void setup(){ pinMode(LED_PIN,OUTPUT); Serial.begin(115200); }
void loop(){
  uint16_t x = touchRead(TOUCH_GPIO);
  bool touched = x < threshold; // En ESP32 clasico, tocar suele reducir valor
  digitalWrite(LED_PIN,touched ? HIGH : LOW);
  Serial.print("tacto=");Serial.println(x);
  delay(100);
}
