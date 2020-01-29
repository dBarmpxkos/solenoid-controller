#define SOLENOID_PIN 9
#define LED_PIN     13

unsigned int delayOn = 0;
unsigned int delayOff = 0;

boolean solenoidState;
unsigned long ms;
unsigned long msLast;
int interval = delayOn;

void setup() {
  Serial.begin(9600);
  pinMode(SOLENOID_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  digitalWrite(SOLENOID_PIN, LOW);
  digitalWrite(LED_PIN, LOW);

  /* "Im ready" */
  Serial.println(">");

}

void loop() {
  digitalWrite(SOLENOID_PIN, solenoidState);
  digitalWrite(LED_PIN, solenoidState);

  if (Serial.available()) {
    char c = Serial.read();
    if (c == '>')
      delayOn = Serial.parseInt();
    if (c == '<')
      delayOff = Serial.parseInt();
  }
  
  dutyCycleSolenoid();
}


void dutyCycleSolenoid(void)
{
  ms = millis();

  if (ms - msLast >= interval) {
    (solenoidState ? interval = delayOff : interval = delayOn);
    solenoidState = !(solenoidState);
    msLast = ms;
  }
}
