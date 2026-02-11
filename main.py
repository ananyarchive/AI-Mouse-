import cv2
import mediapipe as mp
import pyautogui
import pyautogui as pg
import time
import math
mp_hands = mp.solutions.hands
mp_drawings = mp.solutions.drawing_utils

screen_w , screen_h = pg.size()
print("\n gesture control ")
prev_screen_x,prev_screen_y=0,0

#gesture time control
click_start_time = None #to diff between click and long drag (records millisecond for which you hold)
click_times =[]         #what durations you clicked at : to see single or double clicks
click_cooldown = 0.5 #After each click detected, cool down for 0.5 seconds
scroll_mode = False #can't scroll and drag simultaneously
freeze_cursor = False #freeze where click is detected : hand prone to jitter and movements



# Initialize the hands model
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    ret,frame = cap.read() #ret : bool that shows if stream is working or not
    if not ret:
        print ( "can't recieve frame" )
        break
    frame = cv2.flip ( frame, 1) #because webcam shows inverted feed
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawings.draw_landmarks(frame,hand_landmarks,mp_hands.HAND_CONNECTIONS)

            #get finger tips
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]

            fingers = [  #finger upward or curledb
                1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y else 0 #in opencv and mediapipe , "<" holds a different significance. hence if tip(8) < joint(6/0 , it is closer to the top, hence finger pointing upward or finger is curled otherwise
                for tip in [8,12,16,20]
            ]

            #distance between thumb and index
            distance = math.hypot(thumb_tip.x - index_tip.x , thumb_tip.y - index_tip.y)
            if distance < 0.04:
                if not freeze_cursor:
                    freeze_cursor = True
                    click_times.append(time.time())

                    #double click check
                    if len(click_times)>=2 and click_times[-1] - click_times[-2] < 0.4:
                        pg.doubleClick()
                        cv2.putText( frame , "Double Clicked!", (10,50) , cv2.FONT_ITALIC , 1 , (0, 255.255), 2) #double click not able to do properly
                        click_times = [] #starts from the top , resets basically

                    else:
                        pg.click()
                        cv2.putText( frame ,"Single Clicked!" , (10,50) , cv2.FONT_HERSHEY_DUPLEX , 1 ,(0, 255.255) , 2 )
                else:
                    freeze_cursor = False


            #move cursor by index-finger
            if not freeze_cursor:
                screen_x = int( screen_w * index_tip.x)
                screen_y = int(screen_h * index_tip.y)
                pyautogui.moveTo((screen_x,screen_y), duration=0.05)
                prev_screen_x,prev_screen_y  = screen_x,screen_y



            #scroll mode
            if sum(fingers)==4:
                scroll_mode = True
            else:
                scroll_mode = False

            #scroll actions
            if scroll_mode:
                if index_tip.y < 0.4:
                    pg.scroll(60)
                    cv2.putText( frame , " scroll up " , (10,50) , 1 , cv2.FONT_HERSHEY_TRIPLEX, (0,255.255) , 2 )
                elif index_tip.y > 0.6:
                    pg.scroll(-60)
                    cv2.putText(frame, " scroll down ", (10, 50), 1, cv2.FONT_HERSHEY_TRIPLEX, (0, 255.255), 2)

    cv2.imshow("live feed " , frame)
    if cv2.waitKey(1) == ord('b'):  # waitkey : just stop and check
        break                       # ord : just checks computer code equivalent of b
cap.release()
cv2.destroyAllWindows()
