/* INTERFAZ-IA · Semana 12 · Monitor de aceleración 3 ejes
   ESP32 clásico DOIT DEVKIT V1, ADXL335 en GPIO39/34/35 (ADC1).
   Las tres conversiones son secuenciales, NO simultáneas.
   Protocolo: FRAME,micros,X_mV,Y_mV,Z_mV\n a 115200 bps.
   Comandos por serial: S = transmitir, P = pausar, ? = estado.
   Frecuencia objetivo 250 tramas/s. Medir la tasa efectiva en el PC.
   ADVERTENCIA: alimentación ADXL335 según placa GY-61, GND común y
   ninguna entrada ADC fuera del rango permitido de la placa.
*/
const int PIN_X=39, PIN_Y=34, PIN_Z=35;
const uint32_t PERIODO_US=4000; // 250 Hz
uint32_t siguiente=0;
bool transmitiendo=false;
void setup(){
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_X,ADC_11db);
  analogSetPinAttenuation(PIN_Y,ADC_11db);
  analogSetPinAttenuation(PIN_Z,ADC_11db);
  siguiente=micros()+PERIODO_US;
  Serial.println("# ADXL335_LISTO. Envie S para iniciar, P para pausar.");
}
void loop(){
  while(Serial.available()){
    char c=(char)Serial.read();
    if(c=='S'||c=='s'){transmitiendo=true;siguiente=micros()+PERIODO_US;}
    if(c=='P'||c=='p'){transmitiendo=false;}
    if(c=='?'){Serial.println(transmitiendo?"# STREAM_ON":"# STREAM_OFF");}
  }
  if(!transmitiendo) { delay(1); return; }
  uint32_t ahora=micros();
  if((int32_t)(ahora-siguiente)<0)return;
  siguiente+=PERIODO_US;
  if((int32_t)(micros()-siguiente)>0){ siguiente=micros()+PERIODO_US; }
  uint32_t marca=micros();
  // Las conversiones son consecutivas. No confundir con ADC simultáneo.
  int x=analogReadMilliVolts(PIN_X);
  int y=analogReadMilliVolts(PIN_Y);
  int z=analogReadMilliVolts(PIN_Z);
  Serial.printf("FRAME,%lu,%d,%d,%d\n",(unsigned long)marca,x,y,z);
}
