import cv2
for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
    if cap.isOpened():
        ret, frame = cap.read()
        status = 'OK' if ret else 'opened but no frame'
        print('Index ' + str(i) + ': ' + status)
        cap.release()