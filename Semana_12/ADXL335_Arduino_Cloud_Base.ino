/* INTERFAZ-IA · Semana 12 · Plantilla para Arduino Cloud
   Esta plantilla requiere el archivo thingProperties.h GENERADO POR
   ARDUINO CLOUD para la Thing de esta práctica; no se entrega un archivo
   con credenciales. Crear variables exactamente con estos nombres:
     ax_g, ay_g, az_g, vib_rms_g : float, read-only, periodica 1 s
     alarma_vibracion : bool, read-only, on-change
   El firmware USB de adquisición continua se entrega por separado.
   El envío a la nube es un RESUMEN de baja tasa, NO un flujo de 250 Hz.
*/
#include "thingProperties.h" // Arduino Cloud lo genera al crear la Thing
#include <math.h>
const int X=39,Y=34,Z=35;
const float SENS_MV_G=300.0f; // Nominal con V_S=3.0 V; sustituir por calibración
float cx=1500,cy=1500,cz=1500;
float sx2=0,sy2=0,sz2=0;
float ux=0,uy=0,uz=0;
uint16_t n=0;
unsigned long ultimo=0,ultimoEnvio=0;
void setup(){
 Serial.begin(115200);
 analogReadResolution(12);
 analogSetPinAttenuation(X,ADC_11db);
 analogSetPinAttenuation(Y,ADC_11db);
 analogSetPinAttenuation(Z,ADC_11db);
 initProperties();
 ArduinoCloud.begin(ArduinoIoTPreferredConnection);
}
void loop(){
 ArduinoCloud.update();
 unsigned long ahora=millis();
 if(ahora-ultimo>=10){ // 100 Hz internos, 1 s de resumen cloud
  ultimo=ahora;
  float x=(analogReadMilliVolts(X)-cx)/SENS_MV_G;
  float y=(analogReadMilliVolts(Y)-cy)/SENS_MV_G;
  float z=(analogReadMilliVolts(Z)-cz)/SENS_MV_G;
  ux+=x;uy+=y;uz+=z;sx2+=x*x;sy2+=y*y;sz2+=z*z;n++;
 }
 if(ahora-ultimoEnvio>=1000 && n>1){
   ultimoEnvio=ahora;
   float mx=ux/n,my=uy/n,mz=uz/n;
   float rx=sqrtf(fmaxf(0.0f,sx2/n-mx*mx));
   float ry=sqrtf(fmaxf(0.0f,sy2/n-my*my));
   float rz=sqrtf(fmaxf(0.0f,sz2/n-mz*mz));
   ax_g=mx;ay_g=my;az_g=mz;
   vib_rms_g=sqrtf(rx*rx+ry*ry+rz*rz);
   alarma_vibracion=(vib_rms_g>0.25f); // umbral didáctico, editable
   Serial.printf("# CLOUD,%.3f,%.3f,%.3f,%.3f,%d\n",ax_g,ay_g,az_g,vib_rms_g,alarma_vibracion);
   n=0;ux=uy=uz=sx2=sy2=sz2=0;
 }
}
