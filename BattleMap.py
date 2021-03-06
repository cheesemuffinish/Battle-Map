# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import win32api, win32con
import time
 
def mv_chk(xPos, yPos, current):
    xAv = 0
    yAv = 0
    for item in xArr:
        xAv = item + xAv
    for item in yArr:
        yAv = item + yAv
    xAv = xAv/10
    yAv = yAv/10
    if np.sqrt((xAv-current[0])**2 + (yAv-current[1])**2) < 10:
        xNew = current[0]
        yNew = current[1]
    else:
        xNew = xAv
        yNew = yAv
    return (xNew,yNew)
    
def find_and_outline(c, color):
        
        ((x, y), radius) = cv2.minEnclosingCircle(c)
 
		# only proceed if the radius meets a minimum size
        if radius > 5 and radius < 20:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                color, 2)
            #cv2.circle(frame, center1, 5, (50, 50, 255), -1)
            

timeClk = 0
    
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
#color1Lower = (59, 93, 168) #green
#color1Upper = (96, 255, 255) #green
#color1Lower = (150, 122, 141) #hot pink
#color1Upper = (174, 255, 255) #hot pink
#color2Lower = (0, 122, 194) #blue
#color2Upper = (47, 255, 255) #blue
color2Lower = (162, 118, 83) #red poker chip
color2Upper = (179, 255, 255) #red poker chip
#color1Lower = (77, 70, 43) #blue poker chip
#color1Upper = (121, 255, 255) #blue poker chip
color1Lower = (0, 0, 0) #white battle mat
color1Upper = (179, 25, 255) #white battle mat
pts = deque(maxlen=args["buffer"])
 
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(2)
 
# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])
    
# keep looping
while True:
	# grab the current frame
    (grabbed, frame) = camera.read()
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
    if args.get("video") and not grabbed:
        break
 

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
    mask1 = cv2.inRange(hsv, color1Lower, color1Upper)
    mask1 = cv2.erode(mask1, None, iterations=2)
    mask1 = cv2.dilate(mask1, None, iterations=2)
    
    mask2 = cv2.inRange(hsv, color2Lower, color2Upper)
    mask2 = cv2.erode(mask2, None, iterations=2)
    mask2 = cv2.dilate(mask2, None, iterations=2)
    	# find contours in the mask and initialize the current
	# (x, y) center of the ball
    cnts1 = cv2.findContours(cv2.bitwise_not(mask1.copy()), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center1 = None
    center2 = None
 
    if len(cnts2) > 0:
        for i in range(0,len(cnts2)):
            find_and_outline(cnts2[i],(0,0,255))
    
    
	# only proceed if at least one contour was found
    if len(cnts1) > 0:
        xArr = []
        yArr = []
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
        for i in range(0,len(cnts1)):
            find_and_outline(cnts1[i],(255,0,0))
            
        
        c = max(cnts1, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center1 = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
        
        xArr.append(center1[0])
        yArr.append(center1[1])
        
        size = 1000
        
        point = (abs(size-center1[0]),center1[1])
        
        if len(xArr) == 10:
            point = mv_check(xArr, yArr, center1)
            rem(xArr[0])
            rem(yArr[0])            
        
    	# loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is (0,0) or pts[i] is (0,0):
            continue
 
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
 
	# show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
	# if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
 
# cleanup the camera and close any open windows
cv2.destroyAllWindows()
camera.release()
