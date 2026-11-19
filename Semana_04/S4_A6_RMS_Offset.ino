/* Semana 4 · A6. RMS total y RMS alterna de onda con offset DC.
   Fuente segura 0..3.0 V en GPIO36; ventana de N muestras.
   RMS_ac = sqrt(E[x²]-E[x]²); RMS_total=sqrt(E[x²]).
*/
#include <Arduino.h>
#include <math.h>
constexpr int PIN_ADC=36, N=200;
uint32_t count=0;double sum=0,sumSq=0;
void setup(){Serial.begin(115200);analogSetPinAttenuation(PIN_ADC,ADC_11db);}
void loop(){
  float v=analogReadMilliVolts(PIN_ADC)*0.001f;
  sum+=v;sumSq+=(double)v*v;count++;
  if(count>=N){
    double mu=sum/N;double rmsTotal=sqrt(sumSq/N);
    double rmsAC=sqrt(fmax(0.0,sumSq/N-mu*mu));
    Serial.print("media_V=");Serial.print(mu,4);
    Serial.print(" RMS_total_V=");Serial.print(rmsTotal,4);
    Serial.print(" RMS_AC_V=");Serial.println(rmsAC,4);
    count=0;sum=0;sumSq=0;
  }
  delay(5); // periodo nominal, no garantizado. Verificar fs real.
}
