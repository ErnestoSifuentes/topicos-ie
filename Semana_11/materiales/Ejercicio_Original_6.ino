#include <WiFi.h>
#include <WebServer.h>

//Se crea una red propia
const char* ssid     = "MiRouterESP32";    // Asigna nombre a la red WiFi a crear
const char* password = "123456789";       // Contraseña de la red

WebServer server (80);                   // Puerto HTTP por defecto

bool EstadoCarga = LOW;           // Variable para manejar el estado de la carga
const int Carga = 23;                // Asigna nombre al GPIO23, pin digital activar/desactivar carga

void setup() {
  Serial.begin(115200);                // Configura puerto serial 
  pinMode(Carga, OUTPUT);
   
  WiFi.softAP(ssid, password);                // Se crea el AP (punto de acceso)
  Serial.println("");
  Serial.println("");
  Serial.print("La red Wi-Fi creada es\t");   // Imprime nombre de la red
  Serial.println(ssid);  
  Serial.print( "La IP del ESP32 es:\t");  
  Serial.println( WiFi.softAPIP() );          // Imprime la IP de fábrica
  
  server.on ("/", Responde_Peticion);        // Llama a función  que atiende petición de clientes
  server.on("/Cargaon", Control_CargaON);
  server.on("/Cargaoff", Control_CargaOFF);
  server.onNotFound(handle_NotFound);
  server.begin();                             // Inicio del servidor, en espera de peticiones de clientes
  Serial.println ("Servidor Http iniciado"); // Imprime mensaje de inicio del servidor
  delay(200);
}
void loop() {
  server.handleClient();
  if(EstadoCarga)
  {digitalWrite(Carga, HIGH);}
  else
  {digitalWrite(Carga, LOW);}
}

void Responde_Peticion() {
  EstadoCarga = LOW;
  Serial.println("Carga Apagada");
  server.send(200, "text/html", Pagina_HTML(EstadoCarga)); 
}

void Control_CargaON() {
  EstadoCarga = HIGH;
  Serial.println("Carga Encendida");
  server.send(200, "text/html", Pagina_HTML(true)); 
}

void Control_CargaOFF() {
  EstadoCarga = LOW;
  Serial.println("Carga Apagada");
  server.send(200, "text/html", Pagina_HTML(false)); 
}

void handle_NotFound(){
  server.send(404, "text/plain", "Not found");
}

String Pagina_HTML(uint8_t Carga_status){
  String ptr = "<!DOCTYPE html> <html>\n";
  ptr +="<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, user-scalable=no\">\n";
  ptr +="<title>Carga Control</title>\n";
  ptr +="<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}\n";
  ptr +="body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;} h3 {color: #444444;margin-bottom: 50px;}\n";
  ptr +=".button {display: block;width: 120px;background-color: #3498db;border: none;color: white;padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;border-radius: 4px;}\n";
  ptr +=".button-on {background-color: #db7734;}\n";          // visite https://www.colorhexa.com/3498db
  ptr +=".button-on:active {background-color: #2980b9;}\n";
  ptr +=".button-off {background-color: #34db77;}\n";
  ptr +=".button-off:active {background-color: #2c3e50;}\n";
  ptr +="p {font-size: 14px;color: #888;margin-bottom: 10px;}\n";
  ptr +="</style>\n";
  ptr +="</head>\n";
  ptr +="<body>\n";
  ptr +="<h1>Mi Servidor Web en clase</h1>\n";
  ptr +="<h2>ESP32 en modo</h2>\n";
  ptr +="<h3>Access Point(AP)</h3>\n\n";
  
   if(Carga_status)
  {ptr +="<h3>\nCarga: Encendida</h3><a class=\"button button-off\" href=\"/Cargaoff\">Apagar</a>\n";}
  else
  {ptr +="<h3>\nCarga: Apagada</h3><a class=\"button button-on\" href=\"/Cargaon\">Encender</a>\n";}
   ptr +="</body>\n";
   ptr +="</html>\n";
   return ptr;
}
