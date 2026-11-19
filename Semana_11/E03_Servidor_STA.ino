// INTERFAZ-IA | Semana 11 | ESP32 clásico DOIT DEVKIT V1
// Laboratorio didáctico, cargas LED a 3.3 V. Nunca conectar la red eléctrica.

#include <WiFi.h>
#include <WebServer.h>
const char* SSID="CAMBIAR_SSID"; const char* CLAVE="CAMBIAR_CLAVE";
WebServer server(80);
void startNetwork(){
 WiFi.mode(WIFI_STA); WiFi.begin(SSID,CLAVE);unsigned long t=millis();
 while(WiFi.status()!=WL_CONNECTED && millis()-t<15000)delay(300);
 if(WiFi.status()==WL_CONNECTED){ Serial.print("IP: ");Serial.println(WiFi.localIP());}
 else Serial.println("Error de red; revise SSID/clave.");
}

void home(){server.send(200,"text/html; charset=utf-8",
 "<!doctype html><meta charset='utf-8'><title>ESP32 HMI</title><h1>Servidor web ESP32</h1><p>Unidad II: comunicacion y supervisión</p>");}
void setup(){Serial.begin(115200);startNetwork();server.on("/",home);server.begin();}
void loop(){server.handleClient();delay(2);}
