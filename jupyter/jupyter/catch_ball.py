import math
import time
import numpy as np
from robocup import field
from robocup import vision
from robocup import switches as s
from robocup import movement as mov
from robocup import commands as comm
from robocup import localization as loc
from multiprocessing import Process, Value

robot_angle = 225


xnum = Value('d', 0.0)
ynum = Value('d', 0.0)
anglenum = Value('d', 0.0)
distnum = Value('d', 0.0)
p1 = Process(target=loc.localize, args=(robot_angle, xnum, ynum, True))
p2 = Process(target=vision.detect_the_ball, args=(anglenum, distnum, False))
p1.start()
#p2.start()
while s.state(0):
    a = 0
comm.set_orientation()
while not s.state(0):
    a = 0
comm.start()
seeball = 0
while True:
    robot_speed = 0.1
    x = xnum.value
    y = ynum.value
    angle = anglenum.value
    dist = distnum.value    
    seeball += 1 if dist > 200 else -1 
    if seeball > 3:
        seebsll = 3
    if seeball < -1:
        seeball = -1
    if (x == -1):
        x = field.x/2 + 0.01
    if (y == -1): 
        y = field.y/2 + 0.01
        
    #print(dist)
    robot_speed = mov.adaptive_speed(max_speed=0.25, min_speed=0, upper_dist=800, lower_dist=400, x=x, y=y, ant=(180+0)%360)    
    '''if seeball > 0 and False:
        ba = mov.robot_angle_to_catch_ball(angle, x, y)
        robot_speed = mov.adaptive_speed(max_speed=0.25, min_speed=0, upper_dist=800, lower_dist=400, x=x, y=y, ant=(180+ba)%360)
        print(robot_speed, ba, end = '\r')
        comm.set_moving_angle(ba, robot_speed)
        a = 9
    else:
        print(x, y, end = '\r')
        mov.move_to(x, y, field.x/2, field.y/2)'''
    comm.set_moving_angle(0, robot_speed)
    print(x, y, robot_speed, 0, end = '\r')
    time.sleep(0.05)
    if not s.state(0):
        while not s.state(0):
            comm.pause()
            time.sleep(0.01)
        comm.start()
