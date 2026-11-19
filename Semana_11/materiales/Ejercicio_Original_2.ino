#include <WiFi.h>

const char* ssid     = "ErnestoTablet"; //"INFINITUMzzky";        // Red WiFi a conectarse
const char* password = "12345678"; //"ae45ee76fb";          // Contraseña de la red

void setup() {
      Serial.begin(115200);                        // Configura puerto serial 
          
      Serial.print("Iniciando conexión con ");     // Imprime mensaje de inicio de conexión a red
      Serial.println(ssid);                       // Imprime nombre de la red 
      WiFi.begin(ssid, password);                // Inicia conexión Wi-Fi con router AP (modem Wi-Fi)
      while (WiFi.status() != WL_CONNECTED) {   // Revisa el estado de conexión con el router
            delay(500);                        // tiempo de espera para conexión exitosa 
            Serial.print("-");                // Imprime un caracter mientras se conecta 
      }
      Serial.println(""); 
      Serial.print("Conectado a\t");              // Imprime mensaje de conexión 
      Serial.println(ssid);                       // Imprime nombre de la red 
      Serial.print("IP asignada por router\t");   // Imprime la IP asignada por el router
      Serial.println(WiFi.localIP());            
}

void loop(){
  
}


