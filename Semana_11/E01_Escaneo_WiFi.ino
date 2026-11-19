// INTERFAZ-IA | Semana 11 | ESP32 clásico DOIT DEVKIT V1
// Laboratorio didáctico, cargas LED a 3.3 V. Nunca conectar la red eléctrica.

#include <WiFi.h>
void setup() { Serial.begin(115200); WiFi.mode(WIFI_STA); WiFi.disconnect(); delay(300); }
void loop() {
  Serial.println("REDES DISPONIBLES (no se muestran contrasenas)");
  int n=WiFi.scanNetworks();
  for(int i=0;i<n;i++) {
    Serial.printf("%d: SSID=%s RSSI=%d dBm Canal=%d\n", i+1, WiFi.SSID(i).c_str(), WiFi.RSSI(i), WiFi.channel(i));
  }
  WiFi.scanDelete(); delay(8000);
}
