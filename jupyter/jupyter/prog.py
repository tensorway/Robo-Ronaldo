import math
import time
import numpy as np
from robocup import field
from robocup import vision
from robocup import switches as s
from robocup import movement as mov
from robocup import commands as comm
from robocup import localization as loc
#from filterpy.kalman import KalmanFilter
from multiprocessing import Process, Value
#from filterpy.common import Q_discrete_white_noise


robot_angle = 225

xnum = Value('d', 0.0)
ynum = Value('d', 0.0)
anglenum = Value('d', 0.0)
distnum = Value('d', 0.0)
sizenum = Value('d', 0.0)
p1 = Process(target=loc.localize, args=(robot_angle, xnum, ynum, False))
p2 = Process(target=vision.detect_the_ball, args=(anglenum, distnum, sizenum, False))
p1.start()
p2.start()


def attacker():
    if seeball > 2:
        robot_speed = 0.3
        ba = mov.robot_angle_to_catch_ball(angle, x, y)
        _, ba = mov.flatten_angle_attacker(upper_dist=1200, x=x, y=y, ant=ba, speed=robot_speed)
        robot_speed, angle_out = mov.adaptive_speed_line_attacker(max_speed=0.4 , min_speed=0, upper_dist=800, x=x, y=y, ant=(ba)%360)
        robot_speed_ball = mov.adaptive_speed_ball(ba, dist, robot_speed, 0.3)
        min_speed = robot_speed if robot_speed_ball > robot_speed else robot_speed_ball
        if angle_out is None:
            comm.set_moving_angle(ba, min_speed)
        else:
            comm.set_moving_angle(angle_out, robot_speed)
    else:
        mov.move_to(x, y, field.x/2+100, field.y/2+350, 0.5)  

def goalief(ball_angle, ball_size, ball_distance, goalie_last_time):
    robot_speed = 0.3
    #print (time.time() - goalie_last_time, ball_distance, seeball)
    if seeball > 2:
        dirr = math.sin(math.radians(ball_angle))
        ba = 0 if ball_angle<0 else 180
        robot_max_speed = 0.4*abs(dirr)
        #ba = mov.robot_angle_to_catch_ball(ball_angle, x, y)
        #print("ba1=", ba)
        ##_, ba = mov.flatten_angle_goalie(upper_dist=800, x=x, y=y, ant=ba, speed=robot_speed)
        #print("ba flat=", ba)
        #robot_speed, ba = mov.goalie_vector_transform(x, y, ba, robot_max_speed)
        ##robot_speed, ba = mov.goalie_vector_transform(x, y, ba, robot_speed)
        robot_speed, angle_out = mov.adaptive_speed_line_goalie(max_speed=robot_max_speed , min_speed=0, upper_dist=200, x=x, y=y, ant=(ba)%360)
        
        
        if ball_distance > 350:
            goalie_last_time = time.time()  
        if time.time() - goalie_last_time  > 7:
            #robot_speed, ba = mov.goalie_vector_transform(x, y, ba, robot_speed)
            attacker()
            return goalie_last_time
        min_speed = robot_speed
        if angle_out is None:
            comm.set_moving_angle(ba, min_speed)
        else:
            comm.set_moving_angle(angle_out, robot_speed)
    else:
        mov.move_to(x, y, field.x/2, 520, 0.7)
        goalie_last_time = time.time()
    return goalie_last_time    
       

while s.state(0):
    a = 0
comm.set_orientation()
while not s.state(0):
    a = 0
comm.start()
x = field.x / 2 + 0.01
y = field.y / 2 + 0.012
seeball = 0
robot_speed = 0.1
goalie = False
goalie_last_time = 0

while True:
    xc = xnum.value
    yc = ynum.value
    angle = anglenum.value
    ball_size = sizenum.value
    dist = distnum.value   

    seeball += 1 if ball_size > 200 else -3 
    if seeball > 10:
        seeball = 10
    if seeball < -1:
        seeball = -1
        
    if (xc != -1):
        x = xc
    if (yc != -1): 
        y = yc
    if not s.state(2):   
        goalie_last_time = goalief(ball_angle = angle, ball_size = ball_size, ball_distance = dist, goalie_last_time=goalie_last_time)
    else:
        attacker()
    #print(x, y, robot_speed, angle, 44, seeball)#,  end = '\r')
    if angle > -10 and angle<10 and dist < 155 and dist > 135 and ball_size > 1300 and ball_size < 1600:#and y > field.y/2:\n",
        comm.kick()
        time.sleep(0.005)
    time.sleep(0.005)
    s.check_pause()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        