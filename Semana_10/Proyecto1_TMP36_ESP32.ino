/* INTERFAZ-IA · Semana 10 · Proyecto 1 · TMP36 y ESP32 clásico DOIT DEVKIT V1
   ADC1 CH0: GPIO36. Indicadores a 3.3 V: GPIO22 frío, GPIO23 calor.
   NO conectar cargas de red ni actuadores directamente a los GPIO.
   Protocolo USB UART 115200: R (o 2) lectura; N apagar; F frío; C calor.
   Retorno de lectura: DATA,cuenta,milivoltios\n
   El firmware apaga las salidas si no recibe comandos durante 3000 ms.
*/
const int PIN_ADC = 36;
const int LED_FRIO = 22;
const int LED_CALOR = 23;
const unsigned long TIMEOUT_SEGURIDAD_MS = 3000;
unsigned long ultimoComando = 0;
char estado = 'N';

void salidas(char nuevo) {
  // Primero apagar ambas para no producir activaciones simultáneas.
  digitalWrite(LED_FRIO, LOW);
  digitalWrite(LED_CALOR, LOW);
  estado = nuevo;
  if (nuevo == 'F') digitalWrite(LED_FRIO, HIGH);
  else if (nuevo == 'C') digitalWrite(LED_CALOR, HIGH);
}

void setup() {
  pinMode(LED_FRIO, OUTPUT);
  pinMode(LED_CALOR, OUTPUT);
  salidas('N');
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_ADC, ADC_11db); // Ajuste para ESP32 clásico
  ultimoComando = millis();
}

void loop() {
  if (millis() - ultimoComando > TIMEOUT_SEGURIDAD_MS && estado != 'N') salidas('N');
  if (!Serial.available()) return;
  char cmd = (char)Serial.read();
  if (cmd == '\n' || cmd == '\r' || cmd == ' ') return;
  cmd = (char)toupper((unsigned char)cmd);
  if (cmd != 'R' && cmd != '2' && cmd != 'N' && cmd != 'F' && cmd != 'C') {
    Serial.println("ERR,COMANDO");
    return;
  }
  ultimoComando = millis();
  if (cmd == 'R' || cmd == '2') {
    int raw = analogRead(PIN_ADC);
    uint32_t mv = analogReadMilliVolts(PIN_ADC);
    Serial.print("DATA,"); Serial.print(raw); Serial.print(','); Serial.println(mv);
  } else {
    salidas(cmd);
    Serial.print("OK,"); Serial.println(estado);
  }
}
