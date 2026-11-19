/* Semana 4 · A4. Adquirir N lecturas y comparar con referencia DMM.
   Las mediciones del DMM se registran en tabla de practica.
*/
#include <Arduino.h>
constexpr int PIN_ADC=36, N=200;
void setup(){Serial.begin(115200);analogReadResolution(12);analogSetPinAttenuation(PIN_ADC,ADC_11db);}
void loop(){
  uint32_t rawSum=0,mvSum=0;uint16_t lo=4095,hi=0;
  for(int i=0;i<N;i++){
    uint16_t x=analogRead(PIN_ADC);uint32_t mv=analogReadMilliVolts(PIN_ADC);
    rawSum+=x;mvSum+=mv;if(x<lo)lo=x;if(x>hi)hi=x;delay(5);
  }
  Serial.print("raw_prom=");Serial.print(rawSum/(float)N,2);
  Serial.print(" raw_min=");Serial.print(lo);
  Serial.print(" raw_max=");Serial.print(hi);
  Serial.print(" V_prom=");Serial.println(mvSum/(1000.0f*N),4);
  delay(1000);
}
