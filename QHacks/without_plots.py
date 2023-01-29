import cv2
import datetime as dt
import numpy as np
import json
import requests
import pandas as pd
import time
import base64
import pygsheets as pygsheets

def get_concussion_level(base64data):   
    # get rid of the characters before the actual base64 data
    for i,char in enumerate(base64data):
        if char == ",":
            base64data = base64data[i+1:]
            break
    
    # decode the base64data and upload it to a video file
    fh = open("vid.mp4", "wb")
    fh.write(base64.b64decode(base64data))
    fh.close()

    # confidence function to ensure only circular areas are detected
    def confident(w, h):
        if (abs(w-h) <= 5):
            return False
        return True

    # difference function to get the difference between the radius of the pupils
    def difference(a, b):
        if (a > b):
            return a-b
        else:
            return b-a


    # load the video file being used by open cv
    cap = cv2.VideoCapture("vid.mp4")

    # start the time count and initialize variables to zero
    ts = time.time()
    rad_diff = 0
    area = 0
    concussion_level = 0
    video_quality = 0

    # while frames are being received from the video file
    while True:

        # take the current frame of the video for analysis
        ret, frame = cap.read()

        # if the frame is empty, break the loop
        if hasattr(frame, 'shape') == False:
            break

        # get the size (in pixels) of the frame
        rows, cols, _ = frame.shape

        # crop the frame to include only the area of interest
        roi = frame[0:rows, 0:cols]

        # convert the frame to grayscale and blur it
        grey_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(grey_frame, (7, 7), 0)

        # threshold the frame and find the contours
        thresh, threshold = cv2.threshold(
            grey_frame, 35, 255, cv2.THRESH_BINARY_INV)
        contours, thresh = cv2.findContours(
            threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # sort the contours by area size
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

        # initialze the areas displayed counter to zero, should have a max of 2
        i = 0

        both = True

        # for the first 2 contours in the sorted array:
        for cnt in contours:

            # create a rectangle around the contour
            (x, y, w, h) = cv2.boundingRect(cnt)

            # if the contour is not circular, break the loop
            if (confident(w, h)) or both is False:
                both = False
                video_quality += 1
                break

            # get the center point of the contour
            centerpoint = (int(x + w/2), int(y + h/2))

            # draw a circle around the contour using the greater dimension (height or width)
            if (h >= w):
                cv2.circle(roi, centerpoint, int(h/2), (255, 0, 0), -1)

                rad = int(h/2)
            else:
                cv2.circle(roi, centerpoint, int(w/2), (255, 0, 0), -1)
                rad = int(w/2)

            # draw a rectangle around the contour
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # if it is the first of 2 contours, save the radius
            if (i == 0):
                temp = rad

            # if its the second of two contours, get the difference in radius by normalizing with respect to the larger radius
            elif (temp > 0):
                rad = rad/temp
                temp = 1

                # calculate the difference
                rad_diff = difference(temp, rad)

                # if the difference is greater than 1, add it to the total area counter (effectively integrating)
                # must be less than one because that is the max difference allowed by normalization - filters out error
                if (rad_diff <= 1):
                    print(rad_diff)
                    area += rad_diff

            # increment counter or break if necessary
            i += 1
            if i == 2:
                break

        # display the frames
        cv2.imshow("Threshold", threshold)
        cv2.imshow("Frame", frame)
        cv2.imshow("grey_frame", grey_frame)
        cv2.imshow("ROI", roi)

        # if the q key is pressed, break the loop
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # end timestamp and calculate the area adjusted for time
    te = time.time()
    area_adjusted = area/(te-ts)

    print(area_adjusted)

    if (video_quality < 20):
        # determine the level of concussion based on the area adjusted
        if (area_adjusted > 9):
            print("you are very concussed")
            concussion_level = 3

        elif (10 > area_adjusted > 7.5):
            print("Concussion likely, complete this questionare")
            concussion_level = 2

        else:
            print("Concussion unlikely, complete this questionare for verification")
            concussion_level = 1
    else:
        print("Video quality is too low to determine concussion level, please reupload a new video")
        concussion_level = -1

    cv2.destroyAllWindows()


    # open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    gc = pygsheets.authorize(service_file='creds.json')
    sh = gc.open('QHacks')
    wks = sh.sheet1
    wks.update_value("A1", concussion_level)

    print(concussion_level)