import math
from robocup import field
from robocup import localization as loc
from robocup import simulate_lidar as sim
from robocup import commands as comm

lines_full = [
    [260, 260, 570, 260],
    [570, 260, 570, 410],
    [570, 410, 660, 520],
    [660, 520, 1160, 520],
    [1160, 520, 1250, 410],
    [1250, 410, 1250, 260],
    [1250, 260, 1560, 260],
    [1560, 260, 1560, 2170],
    [1560, 2170, 1250, 2170],
    [1250, 2170, 1250, 2020],
    [1250, 2020, 1160, 1910],
    [1160, 1910, 660, 1910],
    [660, 1910, 570, 2020],
    [570, 2020, 570, 2170],
    [570, 2170, 260, 2170],
    [260, 2170, 260, 260]
]

lines = [
    [260, 260, 570, 260],
    [570, 260, 570, 410],
    [570, 410, 660, 520],
    [660, 520, 1160, 520],
    [1160, 520, 1250, 410],
    [1250, 410, 1250, 260],
    [1250, 260, 1560, 260],
    [1560, 260, 1560, 2070],
    [1560, 2070, 1250, 2070],
    [1250, 2070, 1250, 1920],
    [1250, 1920, 1160, 1810],
    [1160, 1810, 660, 1810],
    [660, 1810, 570, 1920],
    [570, 1920, 570, 2070],
    [570, 2070, 260, 2070],
    [260, 2070, 260, 260]
]

lines_attacker = [
    [260, 650, 560, 750],
    [560, 750, 1360, 750],
    [1360, 750, 1560, 650],
    [1560, 650, 1560, 2070],
    [1560, 2070, 1250, 2070],
    [1250, 2070, 1250, 1920],
    [1250, 1920, 1160, 1810],
    [1160, 1810, 660, 1810],
    [660, 1810, 570, 1920],
    [570, 1920, 570, 2070],
    [570, 2070, 260, 2070],
    [260, 2070, 260, 650]
]

flat_line_attacker = [[260, 650, 560, 750],
                      [560, 750, 1360, 750],
                      [1360, 750, 1560, 650]]

flat_line_goalie =  [[570, 260, 570, 410],
                     [570, 410, 660, 520],
                     [660, 520, 1160, 520],
                     [1160, 520, 1250, 410],
                     [1250, 410, 1250, 260]]

goalie_lines = [[570, 260, 570, 460],
                #[570, 410, 660, 520],
                [570, 460, 1250, 460],
                #[1160, 520, 1250, 410],
                [1250, 460, 1250, 260],
                [1250, 260, 1300, 260],
                [1300, 260, 1300, 610],
                [1300, 610, 520, 610],
                [520, 610, 520, 260]]


def line_dists(x1, y1, segments):
    angles2 = [180, 270, 0, 90]
    scan, points = sim.calc_scan_for_point(x1, y1, angles2, segments)
    return scan


def adaptive_speed_rect(max_speed, min_speed, ball_close_speed, upper_dist, lower_dist, x, y, ant, ball_dist):

    rant = math.radians(ant)
    try:
        math.tan(rant)
    except:
        rant += 0.01
    max_speeds = [0, 0, 0, 0]
    #dists = line_dists(x, y)
    dists = [x, y, field.x - x, field.y - y]
    
    for i in range (len(max_speeds)):
        if dists[i] <= lower_dist:
            #max_speeds[i] = min_speed
            max_speeds[i] = -1
        elif dists[i] <= upper_dist:
            max_speeds[i] = (max_speed - min_speed) / (upper_dist - lower_dist) * (dists[i] - lower_dist) + min_speed;
        else:
            max_speeds[i] = max_speed
            
    out = [0.001, 0.001, 0.0015, 0.0015]
    am_i_out = False
    max_out_dist = 0
    for i in range (4):
        if (max_speeds[i] == -1):
            if (lower_dist - dists[i] > max_out_dist):
                max_out_dist = lower_dist - dists[i]
            out[i] += 1
            am_i_out = True
    if am_i_out:
        angle_to_in = math.degrees(math.atan2(out[1]-out[3], out[0]-out[2]))%360 
        speed = max_out_dist / 200 * 0.3
        if speed > 0.5:
            speed = 0.5
        return speed, angle_to_in
    #print(dists, max_speeds)
            
    x_speed = math.cos(rant)
    y_speed = math.sin(rant)
    speed_to_ret = min_speed
    #print(x_speed, y_speed)
    max_speed_x = max_speeds[2] if x_speed > 0 else max_speeds[0]
    max_speed_y = max_speeds[3] if y_speed > 0 else max_speeds[1]
    #print(max_speed_x, max_speed_y)

    if abs(math.tan(rant)*max_speed_x) <= max_speed_y:
        speed_to_ret = math.sqrt(max_speed_x**2 + (math.tan(rant) * max_speed_x) * (math.tan(rant) * max_speed_x));
    elif abs(1 / math.tan(rant)*max_speed_y) <= max_speed_x:
        speed_to_ret = math.sqrt(max_speed_y * max_speed_y + (1 / math.tan(rant) * max_speed_y) * (1 / math.tan(rant) * max_speed_y));


    if (speed_to_ret < min_speed):
        speed_to_ret = min_speed
        
    if (ant > 10 and ant < 70 or ant > 110 and ant < 150):
        if (ball_dist < 350):
            if (speed_to_ret > ball_close_speed):
                speed_to_ret = ball_close_speed
    return speed_to_ret, None




def adaptive_speed_line(max_speed, min_speed, upper_dist, x, y, ant):

    rant = math.radians(ant)
    try:
        math.tan(rant)
    except:
        rant += 0.01
    max_speeds = [0, 0, 0, 0]
    dists = line_dists(x, y, lines)
    #dists = [x, y, field.x - x, field.y - y]
    
    out = [0.001, 0.001, 0.0015, 0.0015]
    am_i_out = False
    max_out_dist = 0
    
    
    for i in range (len(max_speeds)):
        if dists[i] == -1:
            if (dists[(i+2)%len(dists)] > max_out_dist):
                max_out_dist = dists[(i+2)%len(dists)]
            out[i] += 1
            am_i_out = True
            max_speeds[i] = -1
        elif dists[i] <= upper_dist:
            max_speeds[i] = (max_speed - min_speed) / upper_dist * dists[i] + min_speed;
        else:
            max_speeds[i] = max_speed
            

    if am_i_out:
        angle_to_in = math.degrees(math.atan2(out[1]-out[3], out[0]-out[2]))%360 
        speed = max_out_dist / 200 * 0.3
        if speed > 0.5:
            speed = 0.5
        return speed, angle_to_in
    #print(dists, max_speeds)
            
    x_speed = math.cos(rant)
    y_speed = math.sin(rant)
    speed_to_ret = min_speed
    #print(x_speed, y_speed)
    max_speed_x = max_speeds[2] if x_speed > 0 else max_speeds[0]
    max_speed_y = max_speeds[3] if y_speed > 0 else max_speeds[1]
    #print(max_speed_x, max_speed_y)

    if abs(math.tan(rant)*max_speed_x) <= max_speed_y:
        speed_to_ret = math.sqrt(max_speed_x**2 + (math.tan(rant) * max_speed_x) * (math.tan(rant) * max_speed_x));
    elif abs(1 / math.tan(rant)*max_speed_y) <= max_speed_x:
        speed_to_ret = math.sqrt(max_speed_y * max_speed_y + (1 / math.tan(rant) * max_speed_y) * (1 / math.tan(rant) * max_speed_y));


    if (speed_to_ret < min_speed):
        speed_to_ret = min_speed
        

    return speed_to_ret, None

def adaptive_speed_line_attacker(max_speed, min_speed, upper_dist, x, y, ant):

    rant = math.radians(ant)
    try:
        math.tan(rant)
    except:
        rant += 0.01
    max_speeds = [0, 0, 0, 0]
    dists = line_dists(x, y, lines_attacker)
    #dists = [x, y, field.x - x, field.y - y]
    
    out = [0.001, 0.001, 0.0015, 0.0015]
    am_i_out = False
    max_out_dist = 0
    
    
    for i in range (len(max_speeds)):
        if dists[i] == -1:
            if (dists[(i+2)%len(dists)] > max_out_dist):
                max_out_dist = dists[(i+2)%len(dists)]
            out[i] += 1
            am_i_out = True
            max_speeds[i] = -1
        elif dists[i] <= upper_dist:
            max_speeds[i] = (max_speed - min_speed) / upper_dist * dists[i] + min_speed;
        else:
            max_speeds[i] = max_speed
            

    if am_i_out:
        angle_to_in = math.degrees(math.atan2(out[1]-out[3], out[0]-out[2]))%360 
        speed = max_out_dist / 200 * 0.3
        if speed > 0.5:
            speed = 0.5
        return speed, angle_to_in
    #print(dists, max_speeds)
            
    x_speed = math.cos(rant)
    y_speed = math.sin(rant)
    speed_to_ret = min_speed
    #print(x_speed, y_speed)
    max_speed_x = max_speeds[2] if x_speed > 0 else max_speeds[0]
    max_speed_y = max_speeds[3] if y_speed > 0 else max_speeds[1]
    #print(max_speed_x, max_speed_y)

    if abs(math.tan(rant)*max_speed_x) <= max_speed_y:
        speed_to_ret = math.sqrt(max_speed_x**2 + (math.tan(rant) * max_speed_x) * (math.tan(rant) * max_speed_x));
    elif abs(1 / math.tan(rant)*max_speed_y) <= max_speed_x:
        speed_to_ret = math.sqrt(max_speed_y * max_speed_y + (1 / math.tan(rant) * max_speed_y) * (1 / math.tan(rant) * max_speed_y));


    if (speed_to_ret < min_speed):
        speed_to_ret = min_speed
        

    return speed_to_ret, None


def adaptive_speed_line_goalie(max_speed, min_speed, upper_dist, x, y, ant):

    rant = math.radians(ant)
    try:
        math.tan(rant)
    except:
        rant += 0.01
    max_speeds = [0, 0, 0, 0]
    dists = line_dists(x, y, goalie_lines)
    #dists = [x, y, field.x - x, field.y - y]
    
    out = [0.001, 0.001, 0.0015, 0.0015]
    am_i_out = False
    max_out_dist = 0
    
    
    for i in range (len(max_speeds)):
        if dists[i] == -1:
            if (dists[(i+2)%len(dists)] > max_out_dist):
                max_out_dist = dists[(i+2)%len(dists)]
            out[i] += 1
            am_i_out = True
            max_speeds[i] = -1
        elif dists[i] <= upper_dist:
            max_speeds[i] = (max_speed - min_speed) / upper_dist * dists[i] + min_speed;
        else:
            max_speeds[i] = max_speed
            

    if am_i_out:
        angle_to_in = math.degrees(math.atan2(out[1]-out[3], out[0]-out[2]))%360 
        speed = max_out_dist / 100 * 0.3
        if speed > 0.3:
            speed = 0.3
        return speed, angle_to_in
    #print(dists, max_speeds)
            
    x_speed = math.cos(rant)
    y_speed = math.sin(rant)
    speed_to_ret = min_speed
    #print(x_speed, y_speed)
    max_speed_x = max_speeds[2] if x_speed > 0 else max_speeds[0]
    max_speed_y = max_speeds[3] if y_speed > 0 else max_speeds[1]
    #print(max_speed_x, max_speed_y)

    if abs(math.tan(rant)*max_speed_x) <= max_speed_y:
        speed_to_ret = math.sqrt(max_speed_x**2 + (math.tan(rant) * max_speed_x) * (math.tan(rant) * max_speed_x));
    elif abs(1 / math.tan(rant)*max_speed_y) <= max_speed_x:
        speed_to_ret = math.sqrt(max_speed_y * max_speed_y + (1 / math.tan(rant) * max_speed_y) * (1 / math.tan(rant) * max_speed_y));


    if (speed_to_ret < min_speed):
        speed_to_ret = min_speed
        

    return speed_to_ret, None


def adaptive_speed_ball(angle_to_go, ball_dist, speed, ball_close_speed):
    speed_to_ret = speed
    if (angle_to_go > 0 and angle_to_go < 60 or angle_to_go > 120 and angle_to_go < 180):
        if (ball_dist < 350):
            speed_to_ret = ball_close_speed        
   
    return speed_to_ret

def flatten_angle_attacker(upper_dist, x, y, ant, speed):

    rant = math.radians(ant)
    try:
        math.tan(rant)
    except:
        rant += 0.01
    max_speeds = [0, 0, 0, 0]
    dists = line_dists(x, y, flat_line_attacker)
    #dists = [x, y, field.x - x, field.y - y]
  
    for i in range (len(max_speeds)):
        if dists[i] == -1 or dists[i] >= upper_dist:
            dists[i] = upper_dist

            
    x_speed = math.cos(rant)
    y_speed = math.sin(rant)
    if x_speed < 0:
        x_speed *= dists[0]
    else:
        x_speed *= dists[2]
        
    if y_speed < 0:
        y_speed *= dists[1]
    else:
        y_speed *= dists[3]    
    flat_angle = math.degrees(math.atan2(y_speed, x_speed))%360
    diff = rant - math.radians(flat_angle)
    speed_to_ret = math.cos(diff)*speed
    
    return speed_to_ret, flat_angle

def flatten_angle_goalie(upper_dist, x, y, ant, speed):

    rant = math.radians(ant)
    try:
        math.tan(rant)
    except:
        rant += 0.01
    max_speeds = [0, 0, 0, 0]
    dists = line_dists(x, y, flat_line_goalie)
    #dists = [x, y, field.x - x, field.y - y]
  
    for i in range (len(max_speeds)):
        if dists[i] == -1 or dists[i] >= upper_dist:
            dists[i] = upper_dist

            
    x_speed = math.cos(rant)
    y_speed = math.sin(rant)
    if x_speed < 0:
        x_speed *= dists[0]
    else:
        x_speed *= dists[2]
        
    if y_speed < 0:
        y_speed *= dists[1]
    else:
        y_speed *= dists[3]    
    flat_angle = math.degrees(math.atan2(y_speed, x_speed))%360
    diff = rant - math.radians(flat_angle)
    speed_to_ret = math.cos(diff)*speed
    
    return speed_to_ret, flat_angle


def robot_angle_to_catch_ball(ball_angle, x, y):
    det_side = False
    side = 0                                         #0 left , 1 right
    max_angle = 60
    conv_angle = ball_angle*1.5
    if conv_angle > max_angle:
        conv_angle = max_angle
    if conv_angle < -max_angle:
        conv_angle = -max_angle
    angle_to_go = (ball_angle + conv_angle + 90) % 360


    if (not det_side and ball_angle > 180 + 65 and ball_angle < 360 - 65):
        if (x < field.x/2):
            side = 0
            angle_to_go = ball_angle + 90 + max_angle
        else:
            side = 1
            angle_to_go = ball_angle + 90 - max_angle
        det_side = true
  
    elif (det_side and ball_angle > 180):
        if side:
            angle_to_go = ball_angle + 90 - max_angle
        else:
            angle_to_go = ball_angle + 90 + max_angle
    else:
        det_side = False

    angle_to_go = angle_to_go % 360
    
    return angle_to_go


def goalie_vector_transform(x, y, angle, speed):
    xdev_max = 200
    ydev_max = 200
    xdev_max_speed = 0.2
    ydev_max_speed = 0.2
    xdev_settle = 10
    ydev_settle = 10
    
    dists = line_dists(x, y, flat_line_goalie)
    ydev = dists[1] if dists[1]<ydev_max else ydev_max
    xdev = dists[0] if dists[0]>0 else 0
    xdev = dists[2] if dists[2]>0 else 0
    x_sign = 1 if dists[0]>dists[2] else -1
    xdev = xdev if xdev<xdev_max else xdev_max
    
    xdev = xdev - xdev_settle
    ydev = ydev - ydev_settle
    
    x_speed = speed*math.cos(math.radians(angle))
    y_speed = speed*math.sin(math.radians(angle))
    
    xdev_speed = x_sign * xdev/xdev_max * xdev_max_speed
    ydev_speed = -ydev/ydev_max * ydev_max_speed 
    
    x_sum = x_speed + xdev_speed
    y_sum = y_speed + ydev_speed
    
    angle_to_ret = math.degrees(math.atan2(y_sum, x_sum))%360
    speed_to_ret = math.sqrt(x_sum**2+y_sum**2)
    
    return speed_to_ret, angle_to_ret
                                
                                
    
    
    
    
    

def move_to(x0, y0, x, y, max_speed):
    anglcen = (math.degrees(math.atan2(y-y0, x-x0))) % 360
    spid = math.sqrt((y-y0)**2 + (x-x0)**2)/1500*max_speed + 0.04
    comm.set_moving_angle(anglcen, spid)