/* Semana 4 · A7. Voltimetro serial, barra y alarmas.
   Los umbrales se interpretan dentro del rango util del ADC.
*/
#include <Arduino.h>
constexpr int PIN_ADC=36;constexpr float LOW=0.50f,HIGH=2.80f;
void setup(){Serial.begin(115200);analogSetPinAttenuation(PIN_ADC,ADC_11db);}
void loop(){
  const int N=20;uint32_t sum=0;for(int i=0;i<N;i++){sum+=analogReadMilliVolts(PIN_ADC);delay(1);}
  float v=sum/(1000.0f*N);
  Serial.print("V=");Serial.print(v,3);Serial.print(" [");
  int nb=constrain((int)(v/3.0f*24+0.5f),0,24);
  for(int i=0;i<24;i++)Serial.print(i<nb?'#':' ');
  Serial.print("] ");
  Serial.println(v<LOW?"ALARMA_BAJA":v>HIGH?"ALARMA_ALTA":"OK");
  delay(200);
}
