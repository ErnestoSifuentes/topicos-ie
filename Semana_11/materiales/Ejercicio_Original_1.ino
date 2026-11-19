#include <WiFi.h>


const char* ssid     = "INFINITUMzzky"; // Nombre de la red WiFi
const char* password = "ae45ee76fb";   // Contraseña de la red

WiFiServer server(80); //Servidor Web puerto 80

int contconexion = 0;
String header; // Variable para guardar el HTTP request
String EstadoCarga = "OFF";
const int Carga = 23; // Asigna nombre al GPIO23 

//------------------------CODIGO HTML------------------------------
String pagina = "<!DOCTYPE html>"
"<html>"
"<head>"
"<meta charset='utf-8' />"
"<title>Servidor Web ESP32</title>"
"</head>"
"<body>"
"<center>"
"<h1>Servidor Web ESP32</h1>"
"<p><a href='/on'><button style='height:50px;width:100px'>ON</button></a></p>"
"<p><a href='/off'><button style='height:50px;width:100px'>OFF</button></a></p>"
"</center>"
"</body>"
"</html>";


void setup() {
      Serial.begin(115200);      // Configura puerto serial 
      Serial.println("");
      pinMode(Carga, OUTPUT);    // Configura GPIO23 como salida
      digitalWrite(Carga, LOW);  // Inicia con carga apagada

  // Conexión WIFI
  WiFi.begin(ssid, password);
  //Cuenta hasta 50 si no se puede conectar lo cancela
  while (WiFi.status() != WL_CONNECTED and contconexion <50) { 
    ++contconexion;
    delay(500);
    Serial.print(".");
  }
  if (contconexion <50) {
      Serial.println("");
      Serial.println("WiFi conectado");
      Serial.print("Abra http://");
      Serial.println(WiFi.localIP());
      Serial.println("en cualquier navegador Web");
      server.begin(); // iniciamos el servidor
  }
  else { 
      Serial.println("");
      Serial.println("Error de conexion");
  }
}

//----------------------------LOOP----------------------------------

void loop(){
  WiFiClient client = server.available();   // Escucha a los clientes entrantes

  if (client) {                             // Si se conecta un nuevo cliente
    Serial.println("New Client.");          // 
    String currentLine = "";                //
    while (client.connected()) {            // loop mientras el cliente está conectado
      if (client.available()) {             // si hay bytes para leer desde el cliente
        char c = client.read();             // lee un byte
        Serial.write(c);                    // imprime ese byte en el monitor serial
        header += c;
        if (c == '\n') {                    // si el byte es un caracter de salto de linea
          // si la nueva linea está en blanco significa que es el fin del 
          // HTTP request del cliente, entonces respondemos:
          if (currentLine.length() == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            
             if (header.indexOf("GET /on") >= 0) {
              Serial.println("Carga Encendida");
              EstadoCarga = "ON";
              digitalWrite(Carga, HIGH);
            } else if (header.indexOf("GET /off") >= 0) {
              Serial.println("Carga Apagada");
              EstadoCarga = "OFF";
              digitalWrite(Carga, LOW);
            }
            
            // Muestra la página web
            client.println(pagina);
            
            // la respuesta HTTP temina con una linea en blanco
            client.println();
            break;
          } else { // si tenemos una nueva linea limpiamos currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // si C es distinto al caracter de retorno de carro
          currentLine += c;      // lo agrega al final de currentLine
        }
      }
    }
    // Limpiamos la variable header
    header = "";
    // Cerramos la conexión
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
}


