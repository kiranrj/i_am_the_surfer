import cv2 
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
import pyautogui
import time

count = 0

UP_BOUND        = 180
DOWN_BOUND      = 380
LEFT_TRACK1     = 100
RIGHT_TRACK1    = 400
LEFT_TRACK2     = 450
RIGHT_TRACK2    = 850
LEFT_TRACK3     = 900
RIGHT_TRACK3    = 1150
# LEFT_BOUND    = 500
# RIGHT_BOUND   = 740

# Default bbox
OBJECT_TRACKING_BOUNDS = (456, 170, 337, 435)
ALLOW_ROI_SELECTION = False

DIRECTION_NONE  = 0 
UP              = 1
DOWN            = 2
LEFT            = 3
RIGHT           = 4
CURRENT_DIRECTION = DIRECTION_NONE

TRACK_NONE  = 0
TRACK_1     = 1
TRACK_2     = 2
TRACK_3     = 3
CURRENT_TRACK = TRACK_2

tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
tracker_type = tracker_types[7]

def getTracker() :
    if int(minor_ver) < 3:
        tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        if tracker_type == 'MOSSE':
            tracker = cv2.TrackerMOSSE_create()
        if tracker_type == "CSRT":
            tracker = cv2.legacy.TrackerCSRT_create()
    return tracker

def sendKeyStroke(direction, track):
    global CURRENT_DIRECTION
    if (direction != CURRENT_DIRECTION):
        CURRENT_DIRECTION = direction
        if (direction == UP):
            print("up")
            pyautogui.keyDown('up')
            pyautogui.keyUp('up')
        elif (direction == DOWN):
            print("down")
            pyautogui.keyDown('down')
            pyautogui.keyUp('down')

    global CURRENT_TRACK
    if (track != CURRENT_TRACK):
        if (CURRENT_TRACK > track):
            for i in range(CURRENT_TRACK - track):
                print("left")
                pyautogui.keyDown('left')
                pyautogui.keyUp('left')
        elif (CURRENT_TRACK < track):
            for i in range(track - CURRENT_TRACK):
                print("right")
            pyautogui.keyDown('right')
            pyautogui.keyUp('right')
        # 
        CURRENT_TRACK = track 

    print ("CURRENT_DIRECTION = %d" % CURRENT_DIRECTION)
    print ("CURRENT_TRACK = %d" % CURRENT_TRACK)

def setDirection(img, bbox):
    x,y,w,h= int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    print("x=%d, y=%d, w=%d, h=%d" % (x, y, w, h));
    # Centre of the bounding rectangle
    x = int(x + w/2)
    y = int(y + h/2)
    # print("Center:: x=%d, y=%d" % (x, y));

    global CURRENT_TRACK
    track = CURRENT_TRACK
    direction = DIRECTION_NONE
    # if(x>RIGHT_BOUND):
    #     direction = RIGHT
    # elif(x<LEFT_BOUND):
    #     direction = LEFT
    if (x < RIGHT_TRACK1):
        track = TRACK_1
    elif (x > LEFT_TRACK2 and x < RIGHT_TRACK2):
        track = TRACK_2
    elif (x > LEFT_TRACK3):
        track = TRACK_3

    if(y<UP_BOUND):
        direction = UP
    elif(y>DOWN_BOUND):
        direction = DOWN

    sendKeyStroke(direction, track)
    cv2.circle(img, (x,y), 10, (255, 255, 0), 3)

# Capture a frame to set the ROI
cap = cv2.VideoCapture(0)

bbox = OBJECT_TRACKING_BOUNDS

t_end = time.time() + 10
while time.time() < t_end:
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (255, 0, 0), 2) 
    cv2.imshow('tracking', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if (ALLOW_ROI_SELECTION):
    bbox = cv2.selectROI("tracking", img)

print(bbox)
tracker = getTracker() 
tracker.init(img, bbox)

while True:
    timer= cv2.getTickCount()

    success,img = cap.read()
    img = cv2.flip(img, 1)
    # img_w, img_h = cv2.GetSize(src)
    img_h, img_w, _ = img.shape

    cv2.line(img, (0,UP_BOUND),     (img_w,UP_BOUND),       (0,224,19), 2)
    cv2.line(img, (0,DOWN_BOUND),   (img_w,DOWN_BOUND),     (0,224,19), 2)

    # cv2.line(img, (LEFT_TRACK1,0),   (LEFT_TRACK1,img_h),     (0,224,19), 2)
    cv2.line(img, (RIGHT_TRACK1,0),  (RIGHT_TRACK1,img_h),    (0,224,19), 2)
    cv2.line(img, (LEFT_TRACK2,0),   (LEFT_TRACK2,img_h),     (0,224,19), 2)
    cv2.line(img, (RIGHT_TRACK2,0),  (RIGHT_TRACK2,img_h),    (0,224,19), 2)
    cv2.line(img, (LEFT_TRACK3,0),   (LEFT_TRACK3,img_h),     (0,224,19), 2)
    # cv2.line(img, (RIGHT_TRACK3,0),  (RIGHT_TRACK3,img_h),    (0,224,19), 2)

    success, bbox = tracker.update(img)
    if success:
        setDirection(img, bbox)
    else:
        cv2.putText(img, "lost", (75,50), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,223,0), 2)
        
    fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)
    cv2.putText(img, str(int(fps)), (7,50), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,223,0), 2)

    cv2.imshow("tracking",img)

    if cv2.waitKey(1) == ord('q'):
        break
