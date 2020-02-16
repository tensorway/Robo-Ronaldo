//#include "blu2server2.h"
#define serverq 1 //0- za server ---1 za client
#include "blu2client.h"


#include <bimatrix.h>
#include <motors2020.h>
#include <sensors2020.h>

#define t_non_response 500
#define t_blink_interval 125
#define t_imu_interval 11
#define t_blu_time 100
#define t_matrix_comm 50


long long t_response = 1;
long long t_last_matrix_comm = 0;
bool response = true;
bool response_change = false;
bool state = false;
int t_imu = 0;
int t_blink = 0;
bool found_start = false;
int angle = 0;
float speed = 0;
bool pause_robot = true;
int matrix_comm = -1;
int last_matrix_comm = 0;
//IntervalTimer blinki;
//IntervalTimer imu;

long long t_blu = 0;
char m[4] = {};
int x = 0;
int y = 0;
int goalie = 0;



motors motors;
sensors sensors;
bimatrix bimatrix;


void setup() {
  state = false;
  Serial2.begin(115200);
  Serial.begin(115200);
  Serial2.flush();
  pinMode(2, OUTPUT);
  sensors.imu_set();
  blu_setup();

}

void looop()
{
  //motors.set_moving_angle(0, 0.1);
  motors.turn_motor_on(3);
}

void loop() {


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

    else if (buffer[0] == 'b' && buffer[1] == 'b' && buffer[2] == 'b')
    {
      goalie = buffer[3];
      x = buffer[4];
      y = buffer[5];
    }
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

  if (millis() - t_blu > t_blu_time)
  {
    t_blu = millis();
    m[0] = goalie;
    m[1] = x;
    m[2] = y;
    if (connected)
    {
    communicate(state);
    if (state && serverq)
      set_characteristic(m);       //client
    state = !state;
    }
    else
      goalie_other = 100;
    Serial.print(goalie_other);
    Serial.print(" / ");
    Serial.print(xother);
    Serial.print(" / ");
    Serial.println(yother);
    Serial2.write('b');
    Serial2.write('b');
    Serial2.write('b');
    Serial2.write(goalie_other);
    Serial2.write(xother);
    Serial2.write(yother);
  }




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



