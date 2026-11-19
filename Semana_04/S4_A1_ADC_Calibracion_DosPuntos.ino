/* Semana 4 · A1. Caracterizacion de dos puntos dentro del rango util.
   GPIO36 = ADC1_CH0, ESP32 clasico. Entrada 0..3.3 V ABSOLUTO.
   Para medir, use preferentemente 0.50 y 2.50 V verificados con DMM.
   Los dos puntos NO garantizan corregir la no linealidad del ADC.
   Escriba 0 o 1 por Monitor Serial para captar referencia medida.
*/
#include <Arduino.h>
constexpr int PIN_ADC=36, N=200;
float known[2]={0.50f,2.50f};
float avgRaw[2]={0,0}; bool ready[2]={false,false};
float readAverage(){long s=0;for(int i=0;i<N;++i){s+=analogRead(PIN_ADC);delay(5);}return s/(float)N;}
void setup(){
  Serial.begin(115200);analogReadResolution(12);
  analogSetPinAttenuation(PIN_ADC,ADC_11db);
  Serial.println("Introduzca 0 para 0.50V; 1 para 2.50V, medidos con DMM.");
}
void loop(){
  if(!Serial.available())return;
  int key=Serial.read(); if(key!='0'&&key!='1')return;
  int i=key-'0';avgRaw[i]=readAverage();ready[i]=true;
  Serial.print("Referencia_V=");Serial.print(known[i],3);
  Serial.print(" codigo_promedio=");Serial.println(avgRaw[i],2);
  if(ready[0]&&ready[1]&&avgRaw[1]>avgRaw[0]){
    float m=(known[1]-known[0])/(avgRaw[1]-avgRaw[0]);
    float b=known[0]-m*avgRaw[0];
    Serial.print("m_V_por_cuenta=");Serial.println(m,7);
    Serial.print("b_V=");Serial.println(b,5);
    Serial.println("V_corregido = m*codigo + b (solo interpolacion)");
  }
}
