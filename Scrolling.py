import cv2
import time
import pyautogui
import mediapipe as mp



BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode


MODEL_PATH = "hand_landmarker.task"


options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)


hands = HandLandmarker.create_from_options(options)




SCROLL_SPEED = 300
SCROLL_DELAY = 1

CAM_WIDTH = 640
CAM_HEIGHT = 480




def detect_gesture(landmarks, handedness):

    fingers = []

    tips = [8, 12, 16, 20]

    for tip in tips:

        if landmarks[tip].y < landmarks[tip - 2].y:
            fingers.append(1)



    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]

    if ((handedness == "Right" and thumb_tip.x > thumb_ip.x)
            or
        (handedness == "Left" and thumb_tip.x < thumb_ip.x)):

        fingers.append(1)


    if sum(fingers) == 5:
        return "scroll_up"

    elif len(fingers) == 0:
        return "scroll_down"

    else:
        return "none"




cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)




last_scroll = 0
previous_time = 0

print("Gesture Scroll Control Active")
print("Open palm: Scroll Up")
print("Fist: Scroll Down")
print("Press 'q' to exit")




while cap.isOpened():


    success, img = cap.read()

    if not success:
        break


    img = cv2.flip(img, 1)


    h, w = img.shape[:2]


    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)



    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_img
    )



    timestamp_ms = int(time.time() * 1000)



    results = hands.detect_for_video(
        mp_image,
        timestamp_ms
    )


    # Default values
    gesture = "none"
    handedness = "Unknown"




    if results.hand_landmarks:

        for i, hand_landmarks in enumerate(results.hand_landmarks):


         

            if results.handedness:

                handedness = results.handedness[i][0].category_name


        

            gesture = detect_gesture(
                hand_landmarks,
                handedness
            )


            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),
                (0, 5), (5, 6), (6, 7), (7, 8),
                (5, 9), (9, 10), (10, 11), (11, 12),
                (9, 13), (13, 14), (14, 15), (15, 16),
                (13, 17), (17, 18), (18, 19), (19, 20),
                (0, 17)
            ]


            # Draw connections
            for start, end in connections:

                x1 = int(hand_landmarks[start].x * w)
                y1 = int(hand_landmarks[start].y * h)

                x2 = int(hand_landmarks[end].x * w)
                y2 = int(hand_landmarks[end].y * h)

                cv2.line(
                    img,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )



            for landmark in hand_landmarks:

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                cv2.circle(
                    img,
                    (x, y),
                    5,
                    (255, 0, 0),
                    cv2.FILLED
                )



            current_time = time.time()


            if current_time - last_scroll > SCROLL_DELAY:

                if gesture == "scroll_up":

                    pyautogui.scroll(SCROLL_SPEED)

                    last_scroll = current_time


                elif gesture == "scroll_down":

                    pyautogui.scroll(-SCROLL_SPEED)

                    last_scroll = current_time




    current_time = time.time()

    if current_time - previous_time > 0:

        fps = 1 / (current_time - previous_time)

    else:

        fps = 0

    previous_time = current_time



    cv2.putText(
        img,
        f"FPS: {int(fps)} | Hand: {handedness} | Gesture: {gesture}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2
    )




    cv2.imshow(
        "Gesture Control",
        img
    )



    if cv2.waitKey(1) & 0xFF == ord("q"):

        break



cap.release()

cv2.destroyAllWindows()

hands.close()