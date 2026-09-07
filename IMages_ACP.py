import cv2, time, numpy as np
import mediapipe as mp

Base=mp.tasks.BaseOptions
Landmarker=mp.tasks.vision.HandLandmarker
Options=mp.tasks.vision.HandLandmarkerOptions
Mode=mp.tasks.vision.RunningMode

options=Options(
    base_options=Base(model_asset_path="hand_landmarker.task"),
    running_mode=Mode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

hands=Landmarker.create_from_options(options)

tips={
    "thumb": 4, "index": 8, "middle": 12,
    "ring": 16, "pinky": 20
}

pairs={
    "middle":("SEPIA", "NEGATIVE"),
    "ring": ("BLUR", "GLITCH"),
    "pinky": ("EDGE", "CARTOON")
}

state={k: 0 for k in pairs}
cur="SEPIA"

DEBOUNCE, CAP_DELAY, TOUCH, PINCH=0.6, 1.2, 30, 20
last_filter=last_capture=0
pinch_on=False

SEPIA=np.array([
    [0.272, 0.534, 0.131],
    [0.349, 0.686, 0.168],
    [0.393, 0.769, 0.189]
])

def apply(img, f):
    if f=="SEPIA":
        return np.clip(cv2.transform(img, SEPIA), 0, 255).astype(np.uint8)
    if f=="NEGATIVE":
        return cv2.bitwise_not(img)
    if f=="BLUR":
        return cv2.GaussianBlur(img, (15, 15), 0)
    if f=="GLITCH":
        h, w=img.shape[:2]
        b, g, r=cv2.split(img)
        return cv2.merge([
            np.roll(b, -int(.02*w), 1),
            g,
            np.roll(r, int(.04*w), 1)
        ])
    if f=="EDGE":
        return cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 80, 100)
    if f=="CARTOON":
        g=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        e=cv2.adaptiveThreshold(
            cv2.medianBlur(g, 7), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
        )
        c=cv2.bilateralFilter(img, 9, 75, 75)
        return cv2.bitwise_and(c, c, mask=e)
    return img

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("Error: Could not access webcam.")

    exit()

cv2.namedWindow("Photo App", cv2.WINDOW_NORMAL)

paused = False

freeze = None

last_time = 0

while True:
    if paused:
        cv2.imshow("Photo App", freeze)
        key=cv2.waitKey(50)&0xFF

        if key==ord('q'):
            break
        if key==27:
            paused=False
            pinch_on=False
            cv2.destroyWindow("Captured")
        continue

    ok, img=cap.read()
    if not ok:
        break

    img=cv2.flip(img, 1)
    h, w=img.shape[:2]

    rgb=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_img=mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    timestamp=time.monotonic_ns()//1_000_000
    if timestamp<=last_time:
        timestamp=last_time+1
    last_time=timestamp

    result=hands.detect_for_video(mp_img, timestamp)
    capture=False

    if result.hand_landmarks:

        lm = result.hand_landmarks[0]

        pts = {

        k: (int(lm[v].x*w), int(lm[v].y*h))

        for k, v in tips.items()

        }

        thumb = pts["thumb"]

        index = pts["index"]

        pinch = (

        abs(thumb[0] - index[0]) < PINCH and

        abs(thumb[1] - index[1]) < PINCH

        )

        now = time.time()

        if pinch and not pinch_on and now - last_capture > CAP_DELAY:

            capture = True

            pinch_on = True

            last_capture = now

        if not pinch:

            pinch_on = False

            finger = next(

                (k for k in pairs

                if abs(thumb[0] - pts[k][0]) < TOUCH

                and abs(thumb[1] - pts[k][1]) < TOUCH),

                None

                )

            if finger and now - last_filter > DEBOUNCE:

                cur = pairs[finger][state[finger]]

                state[finger] ^= 1

                last_filter = now

                print("Filter:", cur)

    out = apply(img, cur)

    if cur == "EDGE":

        out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)

    if capture:

        name = f"picture_{int(time.time())}.jpg"

        cv2.imwrite(name, out)

        print("Saved:", name)

        freeze = out.copy()

        paused = True

        cv2.imshow("Captured", freeze)

    cv2.imshow("Photo App", out)

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break

cap.release()

cv2.destroyAllWindows()

hands.close()