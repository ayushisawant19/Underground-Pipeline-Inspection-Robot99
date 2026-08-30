const int BATTERY_PIN = 35;

void setup() {
  Serial.begin(115200);
  pinMode(BATTERY_PIN, INPUT);
}

void loop() {
  int batAdc = analogRead(BATTERY_PIN);
  float batVolts = (batAdc / 4095.0) * 3.3 * 6.0;
  int batPct = constrain(map(batVolts * 100, 1400, 2100, 0, 100), 0, 100);

  Serial.printf("Battery ADC: %d | Voltage: %.2fV | Percentage: %d%%\n", batAdc, batVolts, batPct);
  delay(1000);
}