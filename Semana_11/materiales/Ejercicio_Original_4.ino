#include <WiFi.h>

const char* ssid     = "INFINITUMzzky"; // Nombre de la red WiFi
const char* password = "ae45ee76fb";   // Contraseña de la red

WiFiServer server (80);                // Puerto 80 de conexion Http por defecto

String header;                         // Variable para guardar el HTTP petición
String EstadoCarga = "OFF";           // Variable para manejar el estado de la carga
const int Carga = 23;                 // Asigna nombre al GPIO23, pin digital activar/desactivar carga

//-------------------CODIGO HTML PARA LA PAGINA DEL NAVEGADOR WEB------------------------------
String paginaWeb = "<!DOCTYPE html>"
"<html>"
"<head>"
"<meta charset='utf-8' />"
"<title> Servidor Web ESP32</title>"
"</head>"
"<body>"
"<center>"
"<h1> Ejercicio 4: Servidor Web ESP32</h1>"
"<p><a href='/ON'><button background-color: red; style='height:100px;width:100px;font-size: 20px'>Carga ON</button></a></p>"
"<p><a href='/OFF'><button style='height:100px;width:100px;font-size: 20px'>Carga OFF</button></a></p>"
"</center>"
"</body>"
"</html>";


void setup() {
      Serial.begin(115200);                // Configura puerto serial 
      Serial.println("");
      pinMode(Carga, OUTPUT);               // Configura GPIO23 como salida
      digitalWrite(Carga, LOW);             // Inicia con carga apagada
       
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
      Serial.print("IP asignada por router\t");   // Imprime la IP asignada por el router Wi-Fi
      Serial.println(WiFi.localIP());   
      
      server.begin();                           // Inicio del servidor, en espera de peticiones de clientes
      Serial.println ("Servidor Http iniciado"); // Imprime mensaje de inicio del servidor
      delay(500);
}

void loop(){
  WiFiClient client = server.available();   // Escucha clientes entrantes

  if (client) {                             // Si se conecta un nuevo cliente
    Serial.println("Nuevo Cliente");          // 
    String currentLine = "";                //
    while (client.connected()) {            // loop mientras el cliente está conectado
      if (client.available()) {             // si hay bytes para leer desde el cliente
        char c = client.read();             // lee un byte
        Serial.write(c);                    // imprime ese byte en el monitor serial
        header += c;
        if (c == '\n') {                    // si el byte es un caracter de salto de linea
           if (currentLine.length() == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            
             if (header.indexOf("GET /ON") >= 0) {
              Serial.println("Carga Encendida");
              EstadoCarga = "ON";
              digitalWrite(Carga, HIGH);
            } else if (header.indexOf("GET /OFF") >= 0) {
              Serial.println("Carga Apagada");
              EstadoCarga = "OFF";
              digitalWrite(Carga, LOW);
            }
            
            client.println(paginaWeb); // Muestra página web
            client.println();
            break;
          } else { 
            currentLine = "";
          }
        } else if (c != '\r') {  
          currentLine += c;      
        }
      }
    }
     header = ""; // Borra variable header
     client.stop(); // Cierra la conexión con el cliente
     Serial.println("Cliente desconectado");
     Serial.println("");
  }
}


