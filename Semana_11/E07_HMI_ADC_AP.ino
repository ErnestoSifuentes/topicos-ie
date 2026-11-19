// INTERFAZ-IA | Semana 11 | ESP32 clásico DOIT DEVKIT V1
// Laboratorio didáctico, cargas LED a 3.3 V. Nunca conectar la red eléctrica.

#include <WiFi.h>
#include <WebServer.h>
const char* AP_SSID="INTERFAZ_IA_ESP32"; const char* AP_CLAVE="labesp3212"; // >= 8 caracteres
WebServer server(80);
void startNetwork(){WiFi.mode(WIFI_AP);bool ok=WiFi.softAP(AP_SSID,AP_CLAVE);
 Serial.printf("AP:%s IP:%s\n",ok?"OK":"ERROR",WiFi.softAPIP().toString().c_str());}

const int ADC_PIN=36; // ADC1, entrada de 0 a 3.3 V: no exceder margen seguro
unsigned long ultimo=0;float voltaje=0;int codigo=0;
void home(){String s="<!doctype html><meta charset='utf-8'><meta http-equiv='refresh' content='2'>";
 s += "<title>HMI ADC ESP32</title><h2>HMI de sensor analógico</h2><p>ADC="+String(codigo);
 s += " cuentas</p><p>Voltaje calibrado estimado="+String(voltaje,3)+" V</p>";
 s += "<small>Lectura de un canal, no instrumento de calibracion.</small>";
 server.send(200,"text/html; charset=utf-8",s);}
void estado(){String json="{\"adc\":"+String(codigo)+",\"voltios\":"+String(voltaje,3)+"}";
 server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",json);}
void setup(){Serial.begin(115200);analogReadResolution(12);analogSetPinAttenuation(ADC_PIN,ADC_11db);
 startNetwork();server.on("/",home);server.on("/api/medida",estado);server.begin();}
void loop(){server.handleClient();if(millis()-ultimo>=100){ultimo=millis();codigo=analogRead(ADC_PIN);
 voltaje=analogReadMilliVolts(ADC_PIN)/1000.0;}
 delay(2);}
