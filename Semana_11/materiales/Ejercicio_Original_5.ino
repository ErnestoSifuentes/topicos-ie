#include <WiFi.h>
#include <WebServer.h>

// Se crea una red propia 
const char* ssid     = "MiRouterESP32";    // Asigna nombre a la red WiFi a crear
const char* password = "123456789";       // Contraseña de la red

WebServer server (80);                   // Puerto HTTP por defecto

void setup() {
      Serial.begin(115200);                               // Configura puerto serial 
      WiFi.softAP(ssid, password);                       // Se crea el AP (punto de acceso)
      Serial.println("");
      Serial.println("");
      Serial.print("La red Wi-Fi creada es\t");   // Imprime nombre de la red
      Serial.println(ssid);  
      Serial.print( "La IP del ESP32 es:\t");  
      Serial.println( WiFi.softAPIP() );             // Imprime la IP de fábrica
      server.on ("/", Responde_Peticion);          // Llama a función  que atiende petición de clientes
      server.begin();                             // Inicio del servidor, en espera de peticiones de clientes
      Serial.println ("Servidor Http iniciado"); // Imprime mensaje de inicio del servidor
      delay(200);
}

void loop(){
  server.handleClient ();            // Servidor activo y gestionando peticiones de clientes
}

String mensaje= "<h1> Mensaje enviado desde un ESP32 en modo AP Hoy </h1>";

void Responde_Peticion () {
server.send (200, "text/html", mensaje);   // Envía mensaje a clientes
}

