// INTERFAZ-IA | Semana 11 | ESP32 clásico DOIT DEVKIT V1
// Laboratorio didáctico, cargas LED a 3.3 V. Nunca conectar la red eléctrica.

#include <WiFi.h>
#include <WebServer.h>
const char* AP_SSID="INTERFAZ_IA_ESP32"; const char* AP_CLAVE="labesp3212"; // >= 8 caracteres
WebServer server(80);
void startNetwork(){WiFi.mode(WIFI_AP);bool ok=WiFi.softAP(AP_SSID,AP_CLAVE);
 Serial.printf("AP:%s IP:%s\n",ok?"OK":"ERROR",WiFi.softAPIP().toString().c_str());}

const int LED=23; bool encendido=false;
void actualizar(bool valor){encendido=valor;digitalWrite(LED,encendido?HIGH:LOW);}
void home(){String s="<!doctype html><meta charset='utf-8'><title>HMI ESP32</title><h2>Control supervisado de LED</h2>";
 s += "<p>Estado: "+String(encendido?"ENCENDIDO":"APAGADO")+"</p>";
 s += "<form action='/on' method='post'><button>ENCENDER</button></form>";
 s += "<form action='/off' method='post'><button>APAGAR</button></form>";
 server.send(200,"text/html; charset=utf-8",s);}
void on(){actualizar(true);server.sendHeader("Location","/");server.send(303);}
void off(){actualizar(false);server.sendHeader("Location","/");server.send(303);}
void setup(){pinMode(LED,OUTPUT);actualizar(false);Serial.begin(115200);startNetwork();
 server.on("/",HTTP_GET,home);server.on("/on",HTTP_POST,on);server.on("/off",HTTP_POST,off);server.begin();}
void loop(){server.handleClient();delay(2);}
