#include <WiFi.h>
#include <WebServer.h>

const char* ssid     = "INFINITUMzzky";        // Red WiFi a conectarse
const char* password = "ae45ee76fb";          // Contraseña de la red

WebServer server (80);                        // Puerto 80 de conexion Http por defecto

void setup() {
      Serial.begin(115200);                        // Configura puerto serial 
      Serial.print("Iniciando conexión con ");    // Imprime mensaje de inicio de conexión a red
      Serial.println(ssid);                      // Imprime nombre de la red 
      WiFi.begin(ssid, password);               // Inicia conexión Wi-Fi con router AP (modem Wi-Fi)
      while (WiFi.status() != WL_CONNECTED) {  // Espera y revisa el estado de conexión al AP 
            delay(500);                        // tiempo de espera para conexión exitosa 
            Serial.print("-");                 // Imprime un caracter mientras se conecta 
      }
      Serial.println(""); 
      Serial.print("Conectado a\t");              // Imprime mensaje de conexión 
      Serial.println(ssid);                       // Imprime nombre de la red 
      Serial.print("IP asignada por router\t");   // Imprime la IP asignada por el router
      Serial.println(WiFi.localIP());   

      server.on ("/", Responde_Peticion);          // Llama a función que atiende petición de clientes
      server.begin();                             // Inicio del servidor, en espera de peticiones de clientes
      Serial.println ("Servidor Http iniciado"); // Imprime mensaje de inicio del servidor
      delay(500);
}

void loop(){
  server.handleClient ();                       // Servidor activo y gestionando peticiones de clientes
}

String mensaje = "<h1> Mensaje enviado desde un ESP32 en modo STA </h1>";

void Responde_Peticion () {
server.send (200, "text/html", mensaje);   // Envía mensaje a clientes
}
