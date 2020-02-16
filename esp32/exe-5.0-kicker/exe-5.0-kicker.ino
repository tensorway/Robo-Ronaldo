#include <bimatrix.h>
#include <motors20202.h>
#include <sensors20202.h>

#define t_non_response 500
#define t_blink_interval 125
#define t_imu_interval 11
#define t_matrix_comm 50
#define t_delta_kick 5000
#define kick_duration 100
#define kicker_pin 18
#define kicker_button_pin 19

long long t_response = 1;
long long t_last_matrix_comm = 0;
bool response = true;
bool response_change = false;
bool state = false;
int t_imu = 0;
int t_blink = 0;
bool kick = false;
bool kicking = false;
long long t_last_kick = 0;
bool found_start = false;
int angle = 0;
float speed = 0;
bool pause_robot = true;
int matrix_comm = -1;
int last_matrix_comm = 0;



motors motors;
sensors sensors;
bimatrix bimatrix;


void setup() {
  pinMode(kicker_button_pin, INPUT_PULLUP);
  pinMode(kicker_pin, OUTPUT);
  digitalWrite(kicker_pin, HIGH);
  Serial2.begin(115200);
  Serial.begin(115200);
  Serial2.flush();
  pinMode(2, OUTPUT);
  sensors.imu_set();

}

void looop()
{
  //motors.set_moving_angle(0, 0.1);
  motors.turn_motor_on(1);
}

void loop() {

  kick = !digitalRead(kicker_button_pin);
  if (!pause_robot)
    motors.set_moving_angle(angle, speed);
  else
  {
    sensors.set_pid_error_to_zero(&motors);
    motors.set_moving_angle(0, 0);
  }
  //Serial.println("ok");
  char buffer[7] = {};
  while (Serial2.available())
  {
    char r = Serial2.read();
    //Serial2.write(r);
    if (r == 'm')
    {
      found_start = true;
      break;
    }
  }

  if (Serial2.available() >= 7 && found_start)
  {
    for (int i = 0; i < 7; i++)
      buffer[i] = Serial2.read();
    if (Serial2.available() > 40)
      while (Serial2.available() > 0)
        char r = Serial2.read();

    if (buffer[0] == 'u' && buffer[1] == 'u' && buffer[2] == 'u')
    {
      angle = chars2int(buffer[3], buffer[4]);
      speed = chars2int(buffer[5], buffer[6]) / 1000.;
    }
    else if (buffer[0] == 'p' && buffer[1] == 'p' && buffer[2] == 'p')
      pause_robot = true;
    else if (buffer[0] == 's' && buffer[1] == 's' && buffer[2] == 's')
    {
      pause_robot = false;
      sensors.imu_set();
    }
    else if (buffer[0] == 'o' && buffer[1] == 'o' && buffer[2] == 'o')
      sensors.imu_set();
    else if (buffer[0] == 'k' && buffer[1] == 'k' && buffer[2] == 'k')
      kick = true;
    t_response = millis();
    response_change = true;
    found_start = false;
    //Serial.println(speed);
    //Serial.println(angle);
    /*for(int i=0; i<7; i++)
      Serial.println(buffer[i], DEC);
      Serial.println();*/
  }


  if (millis() - t_response > t_non_response)
  {
    bimatrix.draw_red_neutral();
    speed = 0;
    t_response = millis();
    digitalWrite(2, 0);
  }
  else if (response_change)
  {
    //bimatrix.draw_nothing();
    bimatrix.draw_green_smile();
    response_change = false;
    response = true;
  }

  if (millis() - t_imu > t_imu_interval)
  {
    t_imu = millis();
    sensors.imu_read(&motors);
  }

  if (millis() - t_blink > t_blink_interval)
  {
    t_blink = millis();
    state = !state;
    digitalWrite(2, state);
  }

  if (millis() - t_last_matrix_comm > t_matrix_comm && last_matrix_comm != matrix_comm)
  {
    int placeholder = 0;
    last_matrix_comm = matrix_comm;
  }


  if (kick && millis() - t_last_kick > t_delta_kick)
  {
    kick = false;
    t_last_kick = millis();
  }

  if (millis() - t_last_kick < kick_duration)
    digitalWrite(kicker_pin, HIGH);
  else
    digitalWrite(kicker_pin, LOW);


}



int chars2int(char a, char b)
{
  int c = (a << 8) + b;
  return c;
}

void imu_interrupt()
{
  sensors.imu_read(&motors);
}



