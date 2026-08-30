const int MQ_GAS_PIN = 34;

void setup() {
  Serial.begin(115200);
  pinMode(MQ_GAS_PIN, INPUT);
}

void loop() {
  int gasRaw = analogRead(MQ_GAS_PIN);
  float ch4Pct = (gasRaw / 4095.0) * 100.0;
  
  Serial.printf("MQ Gas Raw ADC: %d | Est. Concentration: %.2f%%\n", gasRaw, ch4Pct);
  delay(1000);
}