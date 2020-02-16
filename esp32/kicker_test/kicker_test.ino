#define t_delta_kick 5000
#define kick_duration 100
#define kicker_pin 18
#define kicker_button_pin 19

bool kick = false;
bool kicking = false;
long long t_last_kick = 0;



void setup() {
  // put your setup code here, to run once:
  pinMode(kicker_button_pin, INPUT_PULLUP);
  pinMode(kicker_pin, OUTPUT);
  digitalWrite(kicker_pin, HIGH);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(digitalRead(19));
  delay(30);
  kick = !digitalRead(kicker_button_pin);

  if (kick && millis() - t_last_kick > t_delta_kick)
  {
    kick = false;
    t_last_kick = millis();
  }

  if (millis() - t_last_kick < kick_duration)
    digitalWrite(kicker_pin, LOW);
  else
    digitalWrite(kicker_pin, HIGH);
}
