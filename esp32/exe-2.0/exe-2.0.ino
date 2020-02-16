#include <bimatrix.h>
#include <motors2020.h>
#include <sensors2020.h>

#define t_non_response 500
#define t_imu_interval 500
long long t_response = 0;
bool response = true;
bool response_change = false;
bool state = false;
int t_imu = 0;
bool found_start = false;
int angle = 0;
float speed = 0;
//IntervalTimer blinki;
//IntervalTimer imu;


bimatrix bimatrix;
motors motors;
sensors sensors;


void setup() {
  Serial1.begin(115200);
  Serial.begin(115200);
  Serial1.flush();
  pinMode(13, OUTPUT);
  //imu.begin(imu_interrupt,  11000);
  sensors.imu_set();
}

void loop() {

  motors.set_moving_angle(angle, speed);
  //Serial.println(analogRead(A3)/1023.*360);
  char buffer[7] = {};
  while (Serial1.available())
  {
    char r = Serial1.read();
    Serial1.write(r);
    if (r == 'm')
    {
      found_start = true;
      break;
    }
    digitalWrite(13, 1);
  }
  
  if (Serial1.available() > 7 && found_start)
  {
    for (int i = 0; i < 7; i++)
      buffer[i] = Serial1.read();
    if (Serial1.available() > 40)
      while (Serial1.available() > 0)
        char r = Serial1.read();

    if (buffer[0] == 'u' && buffer[1] == 'u' && buffer[2] == 'u')
    {
      angle = chars2int(buffer[3], buffer[4]);
      speed = chars2int(buffer[5], buffer[6]) / 1000;
    }
    t_response = millis();
    response_change = true;
    found_start = false;
    Serial.println(speed);
    Serial.println(angle);
  }


  if (millis() - t_response > t_non_response && response)
  {
    bimatrix.draw_red_neutral();
    speed = 0;
    response = false;
    digitalWrite(13, 0);
  }
  else if (response_change)
  {
    bimatrix.draw_green_smile();
    response_change = false;
    response = true;
  }

/*
  if (millis() - t_imu > t_imu_interval)
  {
    t_imu = millis();
    state = !state;
    digitalWrite(13, state);
  }*/


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





