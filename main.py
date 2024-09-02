import cv2
import math
import numpy as np
from moviepy.editor import VideoFileClip
import datetime

#import
video = "C:\\Users\\Александр\\Videos\\0.0.3\\456.mp4"
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
c=0 # счетчик кадров

object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

def clip(c):
        clip = VideoFileClip(video).subclip(int(c/fps-5), int(c/fps+3))
        clip.write_videofile("C:\\Users\\Александр\\Videos\\0.0.3\\output.mp4")
        cv2.destroyAllWindows()

while True:
    c+=1
    ret, main = cap.read()
    if not ret:
        break

    # Get the current frame size
    height, width, _ = main.shape

    # Resize the frame (optimization for 2k)
    scale_percent = 75
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)
    dim = (new_width, new_height)
    resized = cv2.resize(main, dim, interpolation = cv2.INTER_AREA)

    # Work Zone
    frame = main[40:895, 2075:2550] #for 2k

    mask = object_detector.apply(frame)
    mask = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)

    # blue players detection
    lower_range = np.array([0, 0, 50])
    upper_range = np.array([30, 30, 255])

    #red players detection
    lower_range2 = np.array([150,0,0])
    upper_range2 = np.array([255,30,30])

    #puck detection
    lower_range3 = np.array([0, 0, 0])
    upper_range3 = np.array([10, 10, 10])

    #net detection (disabled)
    lower_range4 = np.array([150, 150, 0])
    upper_range4 = np.array([255, 255, 30])

    #mask zone
    mask1 = cv2.inRange(mask,lower_range,upper_range)
    mask2 = cv2.inRange(mask,lower_range2,upper_range2)
    mask3 = cv2.inRange(mask,lower_range3,upper_range3)
    mask4 = cv2.inRange(mask,lower_range4,upper_range4)
    mask = mask1 | mask2 | mask3 | mask4
    _, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)

    #contours for all types of objects
    contours1, _ = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours2, _ = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours3, _ = cv2.findContours(mask3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours4, _ = cv2.findContours(mask4, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #objects
    red_nets = {'s1':221, 's2':254, 's3':48, 's4':55}
    blue_nets = {'s1':221, 's2':254, 's3':800, 's4':807}

    for contour in contours1:
        (x, y, w, h) = cv2.boundingRect(contour) # преобразование массива из предыдущего этапа в кортеж из четырех координат
        if cv2.contourArea(contour) > 15:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # получение прямоугольника из точек кортежа
            blue = {'s1':contour[0][0][0],'s2':contour[0][0][1]}

    for contour in contours2:
        (x, y, w, h) = cv2.boundingRect(contour) # преобразование массива из предыдущего этапа в кортеж из четырех координат
        if cv2.contourArea(contour) > 15:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # получение прямоугольника из точек кортежа
            red = {'s1':contour[0][0][0],'s2':contour[0][0][1]}

    for contour in contours3:
        (x, y, w, h) = cv2.boundingRect(contour) # преобразование массива из предыдущего этапа в кортеж из четырех координат
        if cv2.contourArea(contour) > 15:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # получение прямоугольника из точек кортежа
            puck = {'s1':contour[0][0][0],'s2':contour[0][0][1]}
    try:
        print(blue,red,puck)

    except:
        pass

    # analyse logic
    try:
        #Goals / Saves / Close shots
        if puck['s1'] in range(red_nets['s1'],red_nets['s2']) and puck['s2'] in range(red_nets['s3'], red_nets['s4']):
            print("detected")
            
            # making videoclip
            clip(c)
            break
        if puck['s1'] in range(blue_nets['s1'],blue_nets['s2']) and puck['s2'] in range(blue_nets['s3'], blue_nets['s4']):
            print("detected")
            
            # making videoclip
            clip(c)
            break
    except:
        pass

        

    # Display the resized frame
    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    

    # Wait for a key press
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break