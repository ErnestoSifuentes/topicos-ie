// INTERFAZ-IA | Semana 11 | ESP32 clásico DOIT DEVKIT V1
// Laboratorio didáctico, cargas LED a 3.3 V. Nunca conectar la red eléctrica.

#include <WiFi.h>
const char* SSID="CAMBIAR_SSID"; const char* CLAVE="CAMBIAR_CLAVE";
void setup() {
  Serial.begin(115200); WiFi.mode(WIFI_STA); WiFi.begin(SSID,CLAVE);
  Serial.print("Conectando"); unsigned long t=millis();
  while(WiFi.status()!=WL_CONNECTED && millis()-t<15000){ delay(400);Serial.print('.');}
  Serial.println();
  if(WiFi.status()==WL_CONNECTED)Serial.print("IP local: "), Serial.println(WiFi.localIP());
  else Serial.println("Conexion fallida: verifique credenciales y red 2.4 GHz.");
}
void loop() {delay(1000);}
