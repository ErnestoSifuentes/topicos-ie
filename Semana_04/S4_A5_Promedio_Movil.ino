/* Semana 4 · A5. Promedio movil: 1,10,20 muestras.
   Compara voltaje crudo y promedio filtrado, en mV.
*/
#include <Arduino.h>
constexpr int PIN_ADC=36, WINDOW=10; // Probar 1,10,20
uint16_t buffer[WINDOW]={0};int indexBuffer=0,nValid=0;uint32_t sum=0;
void setup(){Serial.begin(115200);analogSetPinAttenuation(PIN_ADC,ADC_11db);}
void loop(){
  uint16_t raw=(uint16_t)analogReadMilliVolts(PIN_ADC);
  sum-=buffer[indexBuffer];buffer[indexBuffer]=raw;sum+=raw;
  indexBuffer=(indexBuffer+1)%WINDOW;
  if(nValid<WINDOW)nValid++;
  Serial.print("crudo_mV:");Serial.print(raw);
  Serial.print(" filtrado_mV:");Serial.println(sum/(float)nValid,2);
  delay(30);
}
