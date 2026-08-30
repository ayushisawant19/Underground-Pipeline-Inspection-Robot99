const int TRIG_FRONT = 12;
const int ECHO_FRONT = 13;
const int TRIG_REAR  = 15;
const int ECHO_REAR  = 2;
const int TRIG_LEFT  = 0;
const int ECHO_LEFT  = 4;
const int TRIG_RIGHT = 16;
const int ECHO_RIGHT = 17;

float readDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 26000);
  if (duration == 0) return -1.0;
  return (duration * 0.0343) / 2.0;
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_FRONT, OUTPUT); pinMode(ECHO_FRONT, INPUT);
  pinMode(TRIG_REAR,  OUTPUT); pinMode(ECHO_REAR,  INPUT);
  pinMode(TRIG_LEFT,  OUTPUT); pinMode(ECHO_LEFT,  INPUT);
  pinMode(TRIG_RIGHT, OUTPUT); pinMode(ECHO_RIGHT, INPUT);
}

void loop() {
  float f = readDistance(TRIG_FRONT, ECHO_FRONT);
  float r = readDistance(TRIG_REAR, ECHO_REAR);
  float l = readDistance(TRIG_LEFT, ECHO_LEFT);
  float rt = readDistance(TRIG_RIGHT, ECHO_RIGHT);

  Serial.printf("Front: %.1f cm | Rear: %.1f cm | Left: %.1f cm | Right: %.1f cm\n", f, r, l, rt);
  delay(1000);
}