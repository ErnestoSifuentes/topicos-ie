#include <WiFi.h>
#include <WebServer.h>

//Se crea una red propia
const char* ssid     = "MiRouterESP32";    // Asigna nombre a la red WiFi a crear
const char* password = "123456789";       // Contraseña de la red

WebServer server (80);                   // Puerto HTTP por defecto

int AnalogInA0 = 36;              // Declara entrada analógica (ADC1 CH0)
int Dx = 0 ;                     // Variable para almacenar el valor digital de Vx
float q ;                       //  Variable para almacenar el intervalo de cuantificación del ADC
float Vx ;                     //   Variable para almacenar el valor de Vx 

void setup() {
  Serial.begin(115200);                // Configura puerto serial 
  pinMode(AnalogInA0, INPUT);         // Configura GPIO como entrada 
  
  WiFi.softAP(ssid, password);                // Se crea el AP (punto de acceso)
  Serial.println("");
  Serial.println("");
  Serial.print("La red Wi-Fi creada es\t");   // Imprime nombre de la red
  Serial.println(ssid);  
  Serial.print( "La IP del ESP32 es:\t");  
  Serial.println( WiFi.softAPIP() );          // Imprime la IP de fábrica
  
  server.on ("/", Responde_Peticion);        // Llama a función  que atiende petición de clientes
  server.on("/ADC", Control_ADC);
  server.onNotFound(handle_NotFound);
  server.begin();                             // Inicio del servidor, en espera de peticiones de clientes
  Serial.println ("Servidor Http iniciado"); // Imprime mensaje de inicio del servidor
  delay(200);
}

//Función principal
void loop() {
  server.handleClient();
}

//Función para responder al cliente
void Responde_Peticion() {
  Vx = Lee_ADC(AnalogInA0);                           // Lee Vx (voltaje conectado al CH0 del ADC)
  Serial.print("Vx: ");                               // Imprime Vx en monitor serial
  Serial.println(Vx);
  server.send(200, "text/html", Pagina_HTML(Vx));     // Imprime Vx en la pag del cliente (Navegador Web)
}

//Función para controlar el ADC
void Control_ADC() {                                 // Lee Vx (voltaje conectado al CH0 del ADC)
  Vx = Lee_ADC(AnalogInA0);                          // Imprime Vx en monitor serial
  Serial.print("Vx: ");
  Serial.println(Vx);
  server.send(200, "text/html", Pagina_HTML(Vx));    // Imprime Vx en la pag del cliente (Navegador Web)
}

void handle_NotFound(){
  server.send(404, "text/plain", "Not found");
}

//Función para Leer el ADC
float Lee_ADC(int Canal) {
  Dx = analogRead(Canal);        // Obiene Dx (equivalente digital de Vx,cuentas del ADC) 
  q = 3.3/4095;                  // Obtiene q  (intervalo de cuantificación del ADC) 
  float Vx1 = q*Dx;              // Obtiene Vx  (valor medido de Vx, en volts)
  return Vx1;
}


String Pagina_HTML(float CAD_Valor){
  String ptr = "<!DOCTYPE html> <html>\n";
  ptr +="<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, user-scalable=no\">\n";
  ptr +="<title>Carga Control</title>\n";
  ptr +="<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}\n";
  ptr +="body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;} h3 {color: #444444;margin-bottom: 50px;}\n";
  ptr +=".button {display: block;width: 120px;background-color: #3498db;border: none;color: white;padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;border-radius: 4px;}\n";
  ptr +=".button-on {background-color: #3445db;}\n";          
  ptr +=".button-on:active {background-color: #2980b9;}\n";
  ptr +=".button-off {background-color: #db3445;}\n";         // visite https://www.colorhexa.com/3498db
  ptr +=".button-off:active {background-color: #2c3e50;}\n";
  ptr +="p {font-size: 14px;color: #888;margin-bottom: 10px;}\n";
  ptr +="</style>\n";
  ptr +="</head>\n";
  ptr +="<body>\n";
  ptr +="<h1>Mi Servidor Web</h1>\n";
  ptr +="<h2>ESP32 en modo</h2>\n";
  ptr +="<h3>Access Point(AP)</h3>\n\n";
  
  {ptr +="<h1> Lectura Vx: " + String(CAD_Valor) +"</h1><a class=\"button button-off\" href=\"/ADC\">Actualizar</a>\n";}
   ptr +="</body>\n";
   ptr +="</html>\n";
   return ptr;
}
