import sys
from rplidar import RPLidar
import numpy as np
import time
import math 
import cv2
from robocup import simulate_lidar as sim
from robocup import fields


def polar_line2cart (rho, theta):
    a = math.tan(-math.pi/2 + theta)
    if a > 10000:
        a = 10000
    if a < -10000:
        a = -10000
    sini = math.sin(theta)
    if sini == 0:
        sini = 0.0001
    b = 1/sini*rho
    
    return a, b


def draw_rect_line(img, a, b, side, d1, d2):
    xmax, ymax, _ = np.shape(img)
    xmax -= 1
    ymax -= 1
    x0 = -b/a
    print(a, b, x0)
    x500 = (ymax-b)/a
    coeff = math.sqrt(1-1/(a**2))*side
    print("coeff", coeff)
    x1 = x0 + d1*coeff
    x2 = x0 + (d1+d2)*coeff
    x3 = x500 + (d1+d2)*coeff
    x4 = x500 + d1*coeff

    
    vertices = np.array([[x1, 0], [x2, 0], [x3, ymax], [x4, ymax]], np.int32)
    print(vertices)
    x1 = coor_cap(x1, 0, xmax)
    x2 = coor_cap(x2, 0, xmax)
    x3 = coor_cap(x3, 0, xmax)
    x4 = coor_cap(x4, 0, xmax)
    
    # draw a triangle
    vertices = np.array([[x1, 0], [x2, 0], [x3, ymax], [x4, ymax]], np.int32)
    pts = vertices.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], isClosed=True, color=0 , thickness=1)

    # fill it
    cv2.fillPoly(img, [pts], color=0)
    print(vertices)
    
    return img
   


def coor_cap(x, mini, maxi):
    if x < mini:
        x = mini
    if x > maxi:
        x = maxi
    return x


def side(x, y, rho, theta, f):
    a = 0.001
    if theta == 0:
        theta = 0.01
    a = math.tan(-math.pi/2 + theta)
    if a > 10000:
         a = 10000
    a2 = -1 / a
    #rho*sin(t3.1066861.2188711525664heta) = a * rho*cos(theta) + b
    sini = math.sin(theta)
    if sini == 0:
        sini = 0.001
    b = 1/sini*rho
    b2 = y - a2*x
    #ax + b = a2x  +b2
    x2 = (b2 - b) / (a - a2)
    y2 = x2*a2 + b2
    cv2.line(f,(int(x),int(y)), (int(x2),int(y2)),255,2)
    #print(sini, b)
    #cv2.line(f,(int(x),int(y)), (450,300),255,1)
    #print(a, b, a2, b2, rho, theta, x2, y2, end='\r')
    if x2 > x:
        return True

    return False


def pl_dist_polar2(x, y, rho, theta):
    a = 0
    if theta == 0:
        theta = 0.01
    if math.tan(theta) != 0:
        a = math.tan(-math.pi/2 + theta)
    else:
        a = 0.001
    a2 = -1 / a
    #rho*sin(theta) = a * rho*cos(theta) + b
    sini = math.sin(theta)
    if sini == 0:
        sini = 0.0001
    b = 1/sini*rho
    b2 = y - a2*x
    #ax + b = a2x  +b2
    x2 = (b2 - b) / (a - a2)
    y2 = x2*a2 + b2
    return pp_dist(x, y, x2, y2)


def no(x):
    a = 0


def draw_cross(img, x, y, length, color):
    img = cv2.line(img, (x, y), (x, y + length), color ,2)
    img = cv2.line(img, (x, y), (x, y - length), color ,2)
    img = cv2.line(img, (x, y), (x + length, y), color ,2)
    img = cv2.line(img, (x, y), (x - length, y), color ,2)
    return img


def make_img_from_scan(scan):
    w = 500;
    counter = 0
    f = np.zeros((w, w), np.uint8)
    n = len(scan)
    for i in range (n):
        m = scan[i]
        #print(m[0], m[1], m[2])
        x = w/2 + math.cos(math.radians(m[1]+robot_angle))*m[2]/(scale+0.01)*50
        y = w/2 + math.sin(math.radians(m[1]+robot_angle))*m[2]/(scale+0.01)*50
        if x < w-1 and y < w-1 and x>1 and y >1:
            f[int(y)][int(x)] = 255
            f[int(y)+1][int(x)] = 255
            f[int(y)-1][int(x)] = 255
            f[int(y)][int(x)+1] = 255
            f[int(y)][int(x)-1] = 255
    return f, counter


def inf_t(a):
    if a == float('inf'):
        a = 10000
    if a == float('-inf'):
        a = -10000
    return a
    