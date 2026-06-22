import cv2 as cv
from math import atan2, cos, sin, sqrt, pi
import numpy as np
import cv2


threshold1 = 350
threshold2 = 350
theta=0
r_width = 500
r_height = 300
minLineLength = 5 #10
maxLineGap = 10 #1
k_width = 5
k_height = 5
max_slider = 10

class Arrow_Detection():
    def getOrientation(self,pts, img):
        sz = len(pts)
        data_pts = np.empty((sz, 2), dtype=np.float64)
        for i in range(data_pts.shape[0]):
            data_pts[i,0] = pts[i,0,0]
            data_pts[i,1] = pts[i,0,1]
    
        mean = np.empty((0))
        mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, mean)
        cntr = (int(mean[0,0]), int(mean[0,1]))
        angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
        ang = -int(np.rad2deg(angle)) - 90
        if ang> -210 and ang < -150:
            pass
        else:
            return angle
        
    def runner(self, img):
        edged1 = cv.Canny(img, threshold1, threshold2)
        kernel = np.ones((3, 3))
        img_dilate = cv.dilate(edged1, kernel, iterations=2)
        img_erode = cv.erode(img_dilate, kernel, iterations=1)
        # Convert image to binary
        _, bw = cv.threshold(img_erode, 50, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
        contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
        self.final = []
        for i, c in enumerate(contours):
            area = cv.contourArea(c)
            if area < 7000:
                continue
            angle = self.getOrientation(c, img)
            if angle is not None:
                self.final.append(angle)
        if not self.final:
            return None  # no valid orientation found
        if self.final[0] > 0:
            print("Left")
            return True
        else: 
            print("Right")
            return False
        
"""def black_det(self):
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        return cv2.inRange(self.frame_HSV, lower_black, upper_black)

# Load the image
cap = cv.VideoCapture(0)
arrow = Arrow_Detection()

while True:
    ret, img = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    frame = cv2.flip(frame, -1)  # -1 = flip both horizontal and vertical
    height, width = frame.shape[:2]
    frame = frame[:, width//2:]        # take right half
    height, width = frame.shape[:2]
    black_mask = black_det()
    start_row = height // 3
    end_row = 2 * height // 3
    black_mask_roi = black_mask[start_row:end_row, :]
    contours_black, _ = cv2.findContours(black_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    black_x = None
    MIN_CONTOUR_AREA = 500
    if contours_black:
        largest_black = max(contours_black, key=cv2.contourArea)
        if cv2.contourArea(largest_black) > MIN_CONTOUR_AREA:
            M = cv2.moments(largest_black)
            if M["m00"] != 0:
                black_x = int(M["m10"] / M["m00"])
    if black_x is not None:
        direction = arrow.runner(black_mask_roi)
    print("Direction: ", direction)"""


