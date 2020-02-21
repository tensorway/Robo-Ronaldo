import numpy as np
import cv2
import time as t
import matplotlib.pyplot as plt
import math


xball = -100
yball = -100
rball = -10
balli = 1

def no(x):
    a = 0

def read_trackbars():
    hl = cv2.getTrackbarPos('h', 'low')
    sl = cv2.getTrackbarPos('s', 'low')
    vl = cv2.getTrackbarPos('v', 'low')
    
    hh = cv2.getTrackbarPos('h', 'high')
    sh = cv2.getTrackbarPos('s', 'high')
    vh = cv2.getTrackbarPos('v', 'high')

def setup_trackbars():
    cv2.namedWindow('low')
    cv2.namedWindow('high')
    cv2.createTrackbar('h', 'low', 0, 179, no)
    cv2.createTrackbar('s', 'low', 0, 255, no)
    cv2.createTrackbar('v', 'low', 0, 255, no)
    cv2.createTrackbar('h', 'high', 0, 179, no)
    cv2.createTrackbar('s', 'high', 0, 255, no)
    cv2.createTrackbar('v', 'high', 0, 255, no)
    cv2.createTrackbar('ratio_low', 'low', 100, 300, no)
    cv2.createTrackbar('ratio_high', 'high', 100, 300, no)
    cv2.createTrackbar('epsilon', 'low', 0, 100, no)
    cv2.createTrackbar('pp_low', 'low', 0, 1000, no)
    cv2.createTrackbar('pp_high', 'high', 0, 1000, no)

def draw_cross(img, x, y, length, color):
    img = cv2.line(img, (x, y), (x, y + length), color ,5)
    img = cv2.line(img, (x, y), (x, y - length), color ,5)
    img = cv2.line(img, (x, y), (x + length, y), color ,5)
    img = cv2.line(img, (x, y), (x - length, y), color ,5)
    return img

def detect_the_ball(anglenum, dist, sizenum, debug):
    cap = cv2.VideoCapture(0)
    #cap.set(3,1280);
    #cap.set(4,720);
    #cap.set(4,480)
    #cap.set(3,640)
    #cap.set(3,320);
    #cap.set(4,240);
    __, img = cap.read()
    while(img is None):
        __, img = cap.read()
    __, img = cap.read()
    ymax, xmax, _ = img.shape
    print(img.shape)
    if debug:
        setup_trackbars()
        lowi = np.zeros((200, 200, 3), np.uint8)
        highi = np.zeros((200, 200, 3), np.uint8)
    hl = sl = vl = hh = sh = vh = cx = cy = 0
    hight = [hh, sh, vh]
    lowt = [hl, sl, vl]
    xball = -100
    yball = -100
    rball = -10
    balli = 1
    size_mode = 0
    last_size_mode = 1
    xcen = 303
    ycen = 231
    t2 = t.time()

    while True:
        distance = -1
        ball_ret_size = -1
        reliable = -1
        ball_size = -1
        if size_mode != last_size_mode:
            if size_mode == 1:
                cap.set(3,1280);
                cap.set(4,720); 
            else:
                cap.set(4,480)
                cap.set(3,640)     
            last_size_mode = size_mode
        __, img = cap.read()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hight = np.array([1, 255, 255])
        lowt = np.array([0, 49, 142])
        hight2 = np.array([180, 255, 255])
        lowt2 = np.array([168, 49, 142])
        if debug:
            hl = cv2.getTrackbarPos('h', 'low')
            sl = cv2.getTrackbarPos('s', 'low')
            vl = cv2.getTrackbarPos('v', 'low')

            hh = cv2.getTrackbarPos('h', 'high')
            sh = cv2.getTrackbarPos('s', 'high')
            vh = cv2.getTrackbarPos('v', 'high')

            low_ratio = cv2.getTrackbarPos('ratio_low', 'low')/100
            high_ratio = cv2.getTrackbarPos('ratio_high', 'high')/100
            e = cv2.getTrackbarPos('epsilon', 'low')/100
            low_pp = cv2.getTrackbarPos('pp_low', 'low')
            high_pp = cv2.getTrackbarPos('pp_high', 'high')

            #cv2.circle(img,(350, 220), 100, (0,0,0), -1)

            if 0 != 0:
                hight = np.array([hh, sh, vh], np.uint8)
            highi[:] = [hh, sh, vh]
            highc = cv2.cvtColor(highi, cv2.COLOR_HSV2BGR)

            if 0 != 0:
                lowt = np.array([hl, sl, vl], np.uint8)
            lowi[:] = [hl, sl, vl]
            lowc = cv2.cvtColor(lowi, cv2.COLOR_HSV2BGR)



        #mask = cv2.inRange(hsv, lowt, hight)
        mask1 = cv2.inRange(hsv, lowt, hight)
        mask2 = cv2.inRange(hsv, lowt2, hight2)
        mask = cv2.bitwise_or(mask1, mask2)
        kernel = np.ones((5, 5), np.uint8)/25
        mask = cv2.erode(mask, kernel, 1)
        kernel = np.ones((5, 5), np.uint8)/25
        mask = cv2.dilate(mask, kernel, 1)
        #mask = proc
        res = cv2.bitwise_and(img,img,mask = mask)
        

        img2, con, hier = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(con) > 0:
            max_size = 0
            i_max_size = 0
            for i in range (len(con)):
                cnt = con[i]
                '''
                _, (wr, hr), _ = cv2.minAreaRect(cnt)
                ratio = wr/(hr+0.001) if (wr>hr) else hr/(wr+0.001)
                if ratio > 1.5:
                    continue
                area = cv2.contourArea(cnt)
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                res = cv2.drawContours(res,[box],0,(0,0,255),2)'''
                
                area = cv2.contourArea(cnt)    
                (x,y),r = cv2.minEnclosingCircle(cnt)
                center = (int(x),int(y))
                radius = int(r)
                if r < 8:
                    continue
                round_coeff = area/(r*r*3.14)
                if round_coeff < 0.43:
                    continue
                res = cv2.circle(res,center,radius,(0,255,0),2)
                if area > 10000:
                    continue
                area_coeff = area/500 if area<500 else 1
                #print(area, r, r*r*3.14)
                if max_size < area_coeff+round_coeff+ball_inc(x, y, r):
                    max_size = area_coeff+round_coeff+ball_inc(x, y, r)
                    i_max_size = i
                    #print(area, r, r*r*3.14)
            #print(max_size, i_max_size)
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
            ''''    
            if distance == -1:
                size_mode = 1
            if ball_size > 800:
                size_mode = 0
            if ball_size < 100:
                size_mode = 1'''
            
            


        if debug:
            #res = cv2.bitwise_and(img,img,mask = mask)
            cv2.imshow('low', lowc)
            cv2.imshow('high', highc)
            cv2.imshow('img', img)
            #cv2.imshow('mask', mask)
            cv2.imshow('proc', res)

        angle = math.degrees(math.atan2(yball-ycen, xball-xcen))
        if angle < 0:
            angle = -180 - angle
        else: 
            angle = 180 - angle
        angle = -angle
        if debug:
            print(t.time() - t2, angle, distance, end = '\r')
            t2 = t.time()
        anglenum.value = angle
        dist.value = distance
        sizenum.value = ball_ret_size
        if cv2.waitKey(1) != -1:
            break
        #t.sleep(1)

    cap.release()
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