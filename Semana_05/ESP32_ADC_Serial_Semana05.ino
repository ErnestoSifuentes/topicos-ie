/* UACJ · Tópicos de Ingeniería Eléctrica II | Semana 5
   ESP32 clásico (por ejemplo, ESP32-WROOM-32)
   Entrada ADC1 GPIO36. Potenciómetro 10 kOhm entre 3V3 y GND;
   cursor a GPIO36. No exceder 3.3 V; no aplicar voltaje negativo. Rango útil depende de atenuación.
   Tramas: t_ms,adc,voltage (voltaje estimado mediante calibración interna; verificar con DMM).
*/
#include <Arduino.h>
constexpr int ADC_PIN = 36;
constexpr unsigned long SAMPLE_MS = 100UL;
unsigned long nextSample = 0UL;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // 0 ... 4095
  analogSetPinAttenuation(ADC_PIN, ADC_11db);
  nextSample = millis() + SAMPLE_MS;
  Serial.println("# UACJ Semana 5: ADC1 GPIO36, 10 Hz");
  Serial.println("t_ms,adc,voltage");
}
void loop() {
  unsigned long now = millis();
  if ((long)(now - nextSample) >= 0) {
    nextSample += SAMPLE_MS;
    if ((long)(now - nextSample) > (long)SAMPLE_MS) nextSample = now + SAMPLE_MS;
    int adc = analogRead(ADC_PIN);
    float v_est = analogReadMilliVolts(ADC_PIN) / 1000.0f; // calibración incorporada, verificar con DMM
    Serial.print(now);
    Serial.print(',');
    Serial.print(adc);
    Serial.print(',');
    Serial.println(v_est, 4);
  }
}
