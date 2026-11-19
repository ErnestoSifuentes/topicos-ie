/* Semana 4 · A3. Visualizacion de formas de onda a baja frecuencia.
   GPIO36 (ADC1). Fuente externa: 0 <= Vin <= 3.3 V, SIN NEGATIVOS.
   Revise offset/amplitud en osciloscopio antes de conectar al ESP32.
   Lecturas espaciadas aproximadamente 5 ms; el tiempo real incluye conversion/serial.
*/
#include <Arduino.h>
constexpr int PIN_ADC=36;
constexpr uint32_t TS_US=5000;
uint32_t nextUs=0;
void setup(){Serial.begin(115200);analogReadResolution(12);analogSetPinAttenuation(PIN_ADC,ADC_11db);nextUs=micros();}
void loop(){
  uint32_t now=micros();
  if((int32_t)(now-nextUs)<0)return;
  nextUs+=TS_US;
  int raw=analogRead(PIN_ADC); uint32_t mv=analogReadMilliVolts(PIN_ADC);
  Serial.print("ADC:");Serial.print(raw);Serial.print(" V_mV:");Serial.println(mv);
}
