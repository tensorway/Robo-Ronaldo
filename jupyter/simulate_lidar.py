import sys
from rplidar import RPLidar
import numpy as np
import time
import math 
import cv2
scale_field = 0.2
robot_angle = -90

goal_wx = 15
goal_wy = 15
field = [
    [0, 0, 0, 2340],
    [0, 0, 1820, 0],
    [0, 2340, 1820, 2340],
    [1820, 0, 1820, 2340],    
]

goal = [
    [610-goal_wx, 246-goal_wy, 610+goal_wx+600, 246-goal_wy],
    [610-goal_wx, 246-goal_wy, 610-goal_wx, 320],
    [610-goal_wx, 320, 610, 320],
    [610, 320, 610, 246],
    [610, 246, 1210, 246],
    [1210, 246, 1210, 320],
    [1210, 320, 1210+goal_wx, 320],
    [1210+goal_wx, 320, 1210+goal_wx, 246-goal_wy]
]

for s in goal:
    field.append(s)    
    
goal2 = []
for l in goal:
    l2 = []
    for i in range (len(l)):
        l2.append(l[i])
    l2[1] = 2340 - l2[1]
    l2[3] = 2340 - l2[3]
    goal2.append(l2 )

for s in goal2:
    field.append(s)
    
field_t = []

for i in range (len(field)):
    a = []
    field_t.append(a)
    for j in range (len(field[i])):
        field_t[i].append(int(field[i][j] * scale_field))
        


def pp_dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

def pl_dist_polar(x, y, rho, theta):
    b = 1/math.cos(theta)*rho
    a = math.tan(theta)
    a = inf_t(a)
    absi = abs(a*x-y+b)
    root = math.sqrt(a**2+1)
    #print(theta, rho)
    #print(a, b, absi, root)
    return absi/root#*(scale+0.01)/50

def ps_dist(x, y, x1, y1, x2, y2):
    k0, l0 = line_from_points(x1, y1, x2, y2)
    k = -1/k0
    l1 = y1 - k*x1
    l2 = y2 - k*x2
    
    cp1 = (y > k*x + l1)
    cp2 = (y > k*x + l2)
    mid = (not cp1 and cp2) or (not cp2 and cp1)
    
    if mid:
        return pl_dist_cart(x, y, k0, l0)
    else:
        return min(pp_dist(x, y, x1, y1), pp_dist(x, y, x2, y2))

def inf_t(a):
    if a == float('inf'):
        a = 10000
    if a == float('-inf'):
        a = -10000
    return a



def pl_dist_cart(x, y, k, l):
    b = l
    a = k
    a = inf_t(a)
    absi = abs(a*x-y+b)
    root = math.sqrt(a**2+1)
    #print(theta, rho)
    #print(a, b, absi, root)
    return absi/root#*(scale+0.01)/50



def line_from_points(x1, y1, x2, y2):
    if x2 - x1 != 0:
        k = (y2-y1)/(x2-x1)
    else: 
        k = 10000*(y2-y1)
    l = y1 - k*x1
    return k, l


def ps_inter(x, y, angle, seg):
    x1 = seg[0]
    y1 = seg[1]
    x2 = seg[2]
    y2 = seg[3]
    if angle == 0 or angle == 180:
        if x1 == x2:
            yp = y
            y11 = y1
            y22 = y2
            if y2 < y1:
                t = y11
                y11 = y2
                y22 = t
            if yp <= y11 or yp >= y22:
                return -1, [0, 0]
            if is_in_direction(x, y, x1, y, angle)==-1:
                return -1, [0, 0]
            return abs(x-x1), [x1, y]
        if y1 == y2:
            return -1, [0, 0]
        yp = y
        y11 = y1
        y22 = y2
        if y2 < y1:
            t = y11
            y11 = y2
            y22 = t
        if yp <= y11 or yp >= y22:
            return -1, [0, 0]
        k2, l2 = line_from_points(x1, y1, x2, y2)
        xp = (yp-l2)/k2
        if is_in_direction(x, y, xp, yp, angle)==-1:
            return -1, [0, 0]        
        return pp_dist(x, y, xp, yp), [xp, yp]
        
    if angle == 90 or angle == 270:
        if x1 == x2:
            return -1, [0, 0]
        if y1 == y2:
            xp = x
            x11 = x1
            x22 = x2
            if x2 < x1:
                t = x11
                x11 = x22
                x22 = t
            if xp <= x11 or xp >= x22:
                return -1, [0, 0]
            if is_in_direction(x, y, x, y1, angle)==-1:
                return -1, [0, 0]    
            return abs(y1-y), [x, y1]
        xp = x
        x11 = x1
        x22 = x2
        if x2 < x1:
            t = x11
            x11 = x22
            x22 = t
        if xp <= x11 or xp >= x22:
            return -1, [0, 0]
        k2, l2 = line_from_points(x1, y1, x2, y2)
        yp = k2*xp + l2
        if is_in_direction(x, y, xp, yp, angle)==-1:
            return -1, [0, 0]        
        return pp_dist(x, y, xp, yp), [xp, yp]      
            
    k1 = math.tan(math.radians(angle))
    l1 = y - k1*x
    
    if x1 == x2:
        xp = x1
        yp = k1*xp + l1
        if y1 > y2:
            t = y1
            y1 = y2
            y2 = t
        if  y1 <= yp and yp <= y2:
            return pp_dist(x, y, xp, yp), [xp, yp]
        return -1, [0, 0]
    
    
    if y1 == y2:
        yp = y1
        xp = (yp - l1)/k1
        if x1 > x2:
            t = x1
            x1 = x2
            x2 = t
        if  x1 <= xp and xp <= x2:
            return pp_dist(x, y, xp, yp), [xp, yp]
        return -1, [0, 0]
        
    
    k2, l2 = line_from_points(x1, y1, x2, y2)
    
    #x*k1 + l1 = x*k2 + l2
    #print("lines ", k1, l1, k2, l2)
    if (k1-k2) == 0:
        #print("parallel")
        return -1, [0, 0]
    xp = (l2-l1)/(k1-k2)
    if x2 < x1:
        t = x2
        x2 = x1
        x1 = t
    if xp < x1 or x2 < xp:
        return -1, [0, 0]
    yp = k1*xp + l1
    dist = pp_dist(x, y, xp, yp)
    #print("coordinates ",  xp, yp)
    if is_in_direction(x, y, xp, yp, angle)==-1:
        return -1, [0, 0]
    return dist, [xp, yp]



def is_in_direction(x, y, x1, y1, angle):
    if angle >= 45 and angle < 135:
        if y1 < y:
            return -1
    elif angle >= 135 and angle < 225:
        if x1 > x:
            return -1
    elif angle >= 225 and angle < 315:
        if y1 > y:
            return -1  
    else:
        if x1 < x:
            return -1
    return 1



def calc_scan_for_point(x, y, angles, field):
    scan = []
    points = []
    for angle in angles:
        mind = 10000
        point = 0
        for seg in field:
            hp = []
            dist = 0
            #print(angle, seg)
            dist, hp = ps_inter(x, y, angle, seg)
            if is_in_direction(x, y, hp[0], hp[1], angle) == -1:
                dist = -1
            #print( dist, hp)
            #print(" ")
            if dist > -1 and mind > dist:
                mind = dist
                point = hp
                point[0] = int(point[0])
                point[1] = int(point[1])
        scan.append(mind)
        points.append(point)
    return scan, points
                

