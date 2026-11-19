/* Semana 4 · A2. Barrido con potenciometro, Serial Plotter.
   GPIO36 cursor del potenciometro; extremos a 3V3/GND.
   Columna voltaje en mV por API calibrada (no escala cruda 3.3*ADC/4095).
*/
#include <Arduino.h>
constexpr int PIN_ADC=36;
void setup(){Serial.begin(115200);analogReadResolution(12);analogSetPinAttenuation(PIN_ADC,ADC_11db);}
void loop(){
  int raw=analogRead(PIN_ADC);
  uint32_t mv=analogReadMilliVolts(PIN_ADC);
  Serial.print("codigo:");Serial.print(raw);
  Serial.print(" voltaje_mV:");Serial.println(mv);
  delay(50);
}
