import numpy as np
import cv2
import matplotlib.pyplot as plt
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from fractions import Fraction


xball = -100
yball = -100
rball = -10
balli = 1


def no(x):
    a = 0

def read_trackbars(l1, h1, l2, h2):
    h1[0] = cv2.getTrackbarPos('h', 'high1')
    h1[1] = cv2.getTrackbarPos('s', 'high1')
    h1[2] = cv2.getTrackbarPos('v', 'high1')
    
    h2[0] = cv2.getTrackbarPos('h', 'high2')
    h2[1] = cv2.getTrackbarPos('s', 'high2')
    h2[2] = cv2.getTrackbarPos('v', 'high2')
    
    l1[0] = cv2.getTrackbarPos('h', 'low1')
    l1[1] = cv2.getTrackbarPos('s', 'low1')
    l1[2] = cv2.getTrackbarPos('v', 'low1')
    
    l2[0] = cv2.getTrackbarPos('h', 'low2')
    l2[1] = cv2.getTrackbarPos('s', 'low2')
    l2[2] = cv2.getTrackbarPos('v', 'low2')

def setup_trackbars():
    cv2.namedWindow('low1')
    cv2.namedWindow('high1')
    cv2.createTrackbar('h', 'low1', 0, 180, no)
    cv2.createTrackbar('s', 'low1', 0, 255, no)
    cv2.createTrackbar('v', 'low1', 0, 255, no)
    cv2.createTrackbar('h', 'high1', 0, 180, no)
    cv2.createTrackbar('s', 'high1', 0, 255, no)
    cv2.createTrackbar('v', 'high1', 0, 255, no)
    
    cv2.namedWindow('low2')
    cv2.namedWindow('high2')
    cv2.createTrackbar('h', 'low2', 0, 180, no)
    cv2.createTrackbar('s', 'low2', 0, 255, no)
    cv2.createTrackbar('v', 'low2', 0, 255, no)
    cv2.createTrackbar('h', 'high2', 0, 180, no)
    cv2.createTrackbar('s', 'high2', 0, 255, no)
    cv2.createTrackbar('v', 'high2', 0, 255, no)


def setup_default_trackbars(l1, h1, l2, h2):
    cv2.namedWindow('low1')
    cv2.namedWindow('high1')
    cv2.setTrackbarPos('h', 'low1', l1[0])
    cv2.setTrackbarPos('s', 'low1', l1[1])
    cv2.setTrackbarPos('v', 'low1', l1[2])
    cv2.setTrackbarPos('h', 'high1', h1[0])
    cv2.setTrackbarPos('s', 'high1', h1[1])
    cv2.setTrackbarPos('v', 'high1', h1[2])
    
    cv2.namedWindow('low2')
    cv2.namedWindow('high2')
    cv2.setTrackbarPos('h', 'low2', l2[0])
    cv2.setTrackbarPos('s', 'low2', l2[1])
    cv2.setTrackbarPos('v', 'low2', l2[2])
    cv2.setTrackbarPos('h', 'high2', h2[0])
    cv2.setTrackbarPos('s', 'high2', h2[1])
    cv2.setTrackbarPos('v', 'high2', h2[2])


def draw_cross(img, x, y, length, color):
    img = cv2.line(img, (x, y), (x, y + length), color ,5)
    img = cv2.line(img, (x, y), (x, y - length), color ,5)
    img = cv2.line(img, (x, y), (x + length, y), color ,5)
    img = cv2.line(img, (x, y), (x - length, y), color ,5)
    return img


def set_camera_modes(camera, res):
    print(camera.resolution)
    camera.resolution = res
    print(camera.resolution)
    #camera.framerate = 30

    time.sleep(1)
    camera.iso = 150
    t = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = t
    #camera.digital_gain = Fraction(1, 1)
    camera.drc_strength = 'off'
    camera.exposure_mode = 'off'
    
def create_not_mask(nnmask, noise):
    nnoise = cv2.bitwise_not(noise)
    nnmask = cv2.bitwise_and(nnmask, nnoise)
    return nnmask
    
    
def detect_the_ball(anglenum, dist, sizenum, recnum, erasenum, debug):
    
    camera = PiCamera()
    res = (640, 480)
    camera.resolution = res
    #camera.framerate = 30
    nnmask = cv2.imread('nnmask.png', 0)

    set_camera_modes(camera, res)
    rawCapture = PiRGBArray(camera, size=res)

    time.sleep(0.1)
    n = 0
    t1 = time.time()
    averf = 10
    nmask = 0
    angle = distance = 0
    ymax, xmax = res

    xball = -100
    yball = -100
    rball = -10
    balli = 1
    size_mode = 0
    last_size_mode = 1
    xcen = 303
    ycen = 231
    wrote = True
    t2 = time.time()
    
    low1 = np.array([0, 120, 60], np.uint8)
    low2 = np.array([170, 120, 60], np.uint8)
    high1 = np.array([10, 255, 255], np.uint8)
    high2 = np.array([180, 255, 255], np.uint8)
    
    if debug:
        setup_trackbars()
        setup_default_trackbars(low1, high1, low2, high2)

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        img = frame.array
        distance = -1
        ball_ret_size = -1
        reliable = -1
        ball_size = -1
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, low1, high1)
        mask2 = cv2.inRange(hsv, low2, high2)
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.bitwise_and(mask, nnmask)
        mask = cv2.erode(mask, np.ones((4, 4))/16)
        mask = cv2.dilate(mask, np.ones((4, 4))/16)
        res = cv2.bitwise_and(img,img,mask = mask)
        
        if recnum.value >0.5:
            wrote = False
            nnmask = create_not_mask(nnmask, mask)
        
        if erasenum.value > 0.5:
            nnmask = np.ones(nnmask.shape, np.uint8)*255

        if not wrote:
            cv2.imwrite('nnmask.png', nnmask)

        img2, con, hier = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(con) > 0:
            max_size = 0
            i_max_size = 0
            for i in range (len(con)):
                cnt = con[i]
                
                area = cv2.contourArea(cnt)    
                (x,y),r = cv2.minEnclosingCircle(cnt)
                center = (int(x),int(y))
                radius = int(r)
                if r < 4:
                    continue
                round_coeff = area/(r*r*3.14)
                if round_coeff < 0.30:
                    continue
                res = cv2.circle(res,center,radius,(0,255,0),2)
                
                
                #area_coeff = area/500 if area<500 else 1
                if max_size < area:#area_coeff+round_coeff+ball_inc(x, y, r):
                    max_size = area#_coeff+round_coeff+ball_inc(x, y, r)
                    i_max_size = i

            if max_size > 0:
                img = cv2.drawContours(img, con[i_max_size], -1, (0,255,0), 1)
                cnt = con[i_max_size]
                M = cv2.moments(cnt)
                xball = int(M['m10']/(M['m00']+0.001))
                yball = int(M['m01']/(M['m00']+0.001))
                res = draw_cross(res, xball, yball, 20, (0, 255, 0))
                reliable = max_size
                ball_size = cv2.contourArea(cnt)  
                ball_ret_size = ball_size
                _,r = cv2.minEnclosingCircle(cnt)
                distance = dist_from_size(r)
            
            

        if debug:

            read_trackbars(low1, high1, low2, high2)
            #cv2.imshow('low1', cv2.cvtColor(low1, cv2.COLOR_HSV2BGR))
            #cv2.imshow('high1', cv2.cvtColor(high1, cv2.COLOR_HSV2BGR))
            #cv2.imshow('low2', cv2.cvtColor(low2, cv2.COLOR_HSV2BGR))
            #cv2.imshow('high2', cv2.cvtColor(high2, cv2.COLOR_HSV2BGR))
            cv2.imshow('nnmask', nnmask)
            cv2.imshow('img', img)
            cv2.imshow('mask', mask)
            cv2.imshow('proc', res)
            print(time.time() - t2, angle, distance, end = '\r')
            t2 = time.time()

        angle = math.degrees(math.atan2(yball-ycen, xball-xcen))
        if angle < 0:
            angle = -180 - angle
        else: 
            angle = 180 - angle
        angle = -angle

        anglenum.value = angle
        dist.value = distance
        sizenum.value = ball_ret_size
        if cv2.waitKey(1) != -1:
            break
        rawCapture.truncate(0)
        #t.sleep(1)

    camera.close()
    cv2.destroyAllWindows()
    
def ball_inc(xb, yb, rb):
    dist = math.sqrt((xball-xb)**2 + (yball-yb)**2 + (rball-rb)**2)
    if dist < 150:
        balli *= 1.2
        if balli > 1.7:
            balli = 1.7
        return balli
    balli = 1
    return balli

def dist_from_size(size):
    #here size iz radius
    ds_pairs = [[100, 100],[150, 26], [190, 24], [260, 22], [370, 12], [470, 11], [1000, 0]]
    dist_from_size = 0
    last_size = 0
    for d, s in ds_pairs:
        #
        if size > s:
            dist_from_size = (dist_from_size*(size-s)+ d*(last_size-size))/(last_size-s)
            break
        last_size = s
        dist_from_size = d
    return dist_from_size