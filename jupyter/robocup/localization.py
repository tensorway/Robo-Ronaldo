import sys
from rplidar import RPLidar
import numpy as np
import time
import math 
import cv2
from robocup import simulate_lidar as sim
from robocup import field


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


def draw_rect_line(img, l, side, d1, d2):
    a, b = polar_line2cart(l[0], l[1])
    #print("hafh", a, b)
    xmax, ymax = np.shape(img)
    xmax -= 1
    ymax -= 1
    x0 = -b/a
    #print(a, b, x0)
    x500 = (ymax-b)/a
    coeff = math.sqrt(1+1/(a**2))*side
    #print("coeff", coeff)
    x1 = x0 + d1*coeff
    x2 = x0 + (d1+d2)*coeff
    x3 = x500 + (d1+d2)*coeff
    x4 = x500 + d1*coeff

    #cv2.line(img,(int(x0),0),(int(x500),ymax),100,2)


    
    vertices = np.array([[x1, 0], [x2, 0], [x3, ymax], [x4, ymax]], np.int32)
    #print(vertices)
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
    #print(vertices)
    
    return img
   


def coor_cap(x, mini, maxi):
    if x < mini:
        x = mini
    if x > maxi:
        x = maxi
    return x


def side_x(x, y, rho, theta, f):
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
    #cv2.line(f,(int(x),int(y)), (int(x2),int(y2)),255,2)
    #print(sini, b)
    #cv2.line(f,(int(x),int(y)), (450,300),255,1)
    #print(a, b, a2, b2, rho, theta, x2, y2, end='\r')
    if x2 > x:
        return True

    return False


def side_y(x, y, rho, theta, f):
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
    #cv2.line(f,(int(x),int(y)), (int(x2),int(y2)),255,2)
    #print(sini, b)
    #cv2.line(f,(int(x),int(y)), (450,300),255,1)
    #print(a, b, a2, b2, rho, theta, x2, y2, end='\r')
    if y2 > y:
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


def make_img_from_scan(scan, robot_angle):
    w = 500;
    counter = 0
    f = np.zeros((w, w), np.uint8)
    n = len(scan)
    for i in range (n):
        m = scan[i]
        #print(m[0], m[1], m[2])
        x = w/2 + math.cos(math.radians(m[1]+robot_angle))*m[2] * field.scale_field
        y = w/2 + math.sin(math.radians(m[1]+robot_angle))*m[2] * field.scale_field
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


def pp_dist(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)


def lines_d (l_test, nms_lines, u_range, v_range):
    mini = 1000;
    #print(nms_lines)
    for l in nms_lines:
        #l = l[0
        temp = dist_rho(l, l_test) / u_range + dist_angl(l_test[1], l[1]) / v_range
        #print("ls" ,l_test, l, dist_rho(l, l_test) / u_range,   dist_angl(l_test[1], l[1]) / v_range)
        if temp < mini:
            mini = temp
    
    #(mini)
    return mini


def dist_angl(a, b):
    x = abs(a-b)
    y = abs(math.pi - a - b)
    if x < y:
        return x
    return y


def dist_angl2(a, b):
    x = abs(a-b)
    y = abs(2*math.pi - a - b)
    if x < y:
        return x
    return y


def dist_rho(l1, l2):
    if l1[0]*l2[0] < 0:
        if l1[1] > math.pi/2 and l2[1] < math.pi/2 or l2[1] > math.pi/2 and l1[1] < math.pi/2:
            return abs(abs(l1[0]) - abs(l2[0]))
    return abs(l1[0] - l2[0])   



def is_on_right(l0, l, d):
    #print("jfsgjsjj")
    t0 = l0[1]
    t1 = l[1]
    if t0 > math.pi:
        t0 -= math.pi
    if t1 > math.pi:
        t1 -= math.pi
        
    dist = dist_angl2(t0, t1)
    if ((dist < d) or ((dist > math.pi/2 -d) and (dist < math.pi/2 + d))):
        #print("deist = ", dist, d, l0, l, t0, t1, dist < d, dist > math.pi/2 -d, (dist < math.pi/2 + d))
        return True
    return False


def draw_line_polar(img, l):
    rho = l[0]
    theta = l[1]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))
    cv2.line(img,(x1,y1),(x2,y2),255,2)
    
    return img

def is_y(l):
    theta = l[1]
    if theta < math.pi/4 or theta > math.pi/4*3:
        return True
    return False

def find_xy(f, w, line_sens, lines_min_dist, right_angle_deviation, add_y_goal):
    x_coor = -1
    y_coor = -1
    lines = cv2.HoughLines(f,2,np.pi/180*2,line_sens)
    nms_lines = []

    if lines is not None:
        for l in lines:
            l = l[0]
            if is_y(l):
                nms_lines.append(l)
                break
        found = False
        for l in lines:
            for rho, theta in l:
                l = l[0]
                if lines_d (l, nms_lines, w*1.41, math.pi) > lines_min_dist:
                    if (not found) or is_on_right(nms_lines[0], l, right_angle_deviation):
                        nms_lines.append(l)
                        found = True
                        draw_line_polar(f, l)


                        dist = pl_dist_polar2(w/2, w/2, rho, theta)
                        dist2 = dist / field.scale_field
                        if is_y(l) and x_coor == -1:
                            if side_x(int(w/2), int(w/2), rho, theta, f):
                                x_coor = field.x - dist2
                            else:
                                x_coor = dist2
                        elif not is_y(l) and y_coor == -1:   
                            if not side_y(int(w/2), int(w/2), rho, theta, f):
                                if add_y_goal:
                                    y_coor = field.y - dist2 - field.field[8][1]
                                else:
                                    y_coor = field.y - dist2
                            else:
                                if add_y_goal:
                                    y_coor = dist2 + field.field[8][1]
                                else:
                                    y_coor = dist2
                        
                        if x_coor!= -1 and y_coor != -1:
                            return x_coor, y_coor, nms_lines
                        
                        #print("x = ", x_coor, "y = ", y_coor, " dist= ", dist, " dist2 = ", dist2)#, end = '\r') #, " rho=", rho, " theta=", theta, " a=", a, " b=", b, " pres=", x0, " rho=", rho, " theta = ", theta, " end " , end='\r')
    return x_coor, y_coor, nms_lines


def get_pos(img):
    w = 500
    f = np.array(img, copy=True)
    f2 = np.array(img, copy=True)
    f3 = np.array(img, copy=True)
    x, y, lines = find_xy(f, w, 5, 0.2, 0.005, False)
    if not lines:
        return -1, -1, f, f2, f3
    return x, y, f, f2, f3
    side = 1
    if side_x(250, 250, lines[0][0], lines[0][1], f):
        side = -1
    f2 = draw_rect_line(f2, lines[0], side, 600*field.scale_field, 620*field.scale_field)
    draw_line_polar(f2, lines[0])
    _, y, lines = find_xy(f2, w, 20, 0.2, 0.005, False)
    if y == -1:
        f3 = draw_rect_line(f3, lines[0], side, 0, 620*field.scale_field)
        f3 = draw_rect_line(f3, lines[0], side, (600+620)*field.scale_field, 800*field.scale_field)
        _, y, lines = find_xy(f3, w, 20, 0.2, 0.005, True)

    return x, y, f, f2, f3


def debug_get_pos(f, f2, f3):
    f = draw_cross(f, 250, 250, 20, 255)
    #f2 = draw_cross(f2, 250, 250, 20, 255)
    #f3 = draw_cross(f3, 250, 250, 20, 255)
    cv2.imshow("f", f)
    #cv2.imshow("f2", f2)
    #cv2.imshow("f3", f3)
    
def localize(robot_angle, x, y, debug):
    w = 500
    try:
        lidar
    except NameError:
        var_exists = False
    else:
        #lidar.stop()
        a = 0
    cv2.destroyAllWindows()
    #print(1)

    while True:
        try:
            #print(2)
            lidar = RPLidar('/dev/ttyUSB0')
            #lidar.stop()
            f = np.zeros((w, w), np.uint8)
            t1 = time.time()   
            accum = 0
            while True:
                try:
                    for scan in lidar.iter_scans():
                        f, c = make_img_from_scan(scan, robot_angle)
                        x.value, y.value, f1, f2, f3 = get_pos(f)
                        #print(x.value, y.value)
                        
                        if debug:
                            debug_get_pos(f1, f2, f3)
                        
                        if cv2.waitKey(1) != -1:
                            cv2.destroyAllWindows()
                            break
                except Exception as e:
                    a = 0
                    print(e.message)
                    #lidar.stop()
                    
                
                  
            cv2.destroyAllWindows()
            lidar.stop()
        
        except:
            a = 0
            #print("ex1")
