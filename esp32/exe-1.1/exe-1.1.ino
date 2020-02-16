#include <bimatrix.h>
#include <motors2020.h>
#include <sensors2020.h>

#define t_non_response 500 
long long t_response = 0;
bool response = true;
bool response_change = false;
  
bimatrix bimatrix;
motors motors;
sensors sensors;


void setup() {
  Serial1.begin(115200);  
  Serial.begin(115200);
  Serial1.flush();
}

void loop() {

  sensors.imu_read(&motors);
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


}

















