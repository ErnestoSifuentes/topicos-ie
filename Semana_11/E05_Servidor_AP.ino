// INTERFAZ-IA | Semana 11 | ESP32 clásico DOIT DEVKIT V1
// Laboratorio didáctico, cargas LED a 3.3 V. Nunca conectar la red eléctrica.

#include <WiFi.h>
#include <WebServer.h>
const char* AP_SSID="INTERFAZ_IA_ESP32"; const char* AP_CLAVE="labesp3212"; // >= 8 caracteres
WebServer server(80);
void startNetwork(){WiFi.mode(WIFI_AP);bool ok=WiFi.softAP(AP_SSID,AP_CLAVE);
 Serial.printf("AP:%s IP:%s\n",ok?"OK":"ERROR",WiFi.softAPIP().toString().c_str());}

void home(){server.send(200,"text/html; charset=utf-8",
 "<!doctype html><meta charset='utf-8'><title>ESP32 HMI</title><h1>Servidor web ESP32</h1><p>Unidad II: comunicacion y supervisión</p>");}
void setup(){Serial.begin(115200);startNetwork();server.on("/",home);server.begin();}
void loop(){server.handleClient();delay(2);}
