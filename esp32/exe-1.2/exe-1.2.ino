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
IntervalTimer blinki;
IntervalTimer imu;

  
bimatrix bimatrix;
motors motors;
sensors sensors;


void setup() {
  Serial1.begin(115200);  
  Serial.begin(115200);
  Serial1.flush();
  pinMode(13, OUTPUT);
  imu.begin(imu_interrupt,  10000);
  sensors.imu_set();
}

void loop() {

  //motors.set_moving_angle(0, 0);
  //Serial.println(analogRead(A3)/1023.*360);
  if (Serial1.available() > 0)
  {
   while(Serial1.available() > 0)
   {
    char  r = Serial1.read();
    Serial.print(r);
    Serial1.print(r);
   }
   Serial.println();
   Serial1.println();
   t_response = millis();
   response_change = true;
   
  }
  

  if (millis() - t_response > t_non_response && response)
  {
    bimatrix.draw_red_neutral();
    response = false;
  }
  else if (response_change)
  {
    bimatrix.draw_green_smile();
    response_change = false;
    response = true;
  }


  if (millis() - t_imu > t_imu_interval)
  {
    t_imu = millis();
    state = !state;
    digitalWrite(13, state);
    sensors.imu_print();
  }


}


void blinks()
{
  state = !state;
  digitalWrite(13, state);
}



int chars2int(char a, char b)
{
  int c = (a << 8) + b; 
}

void imu_interrupt()
{
  sensors.imu_read(&motors);
}





