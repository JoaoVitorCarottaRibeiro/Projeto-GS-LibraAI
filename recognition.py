# recognition.py
import cv2
import joblib
import numpy as np
import mediapipe as mp
from collections import deque
from sklearn.metrics import pairwise_distances

_model = None
_X_train = None 
_cap = None
_buffer = deque(maxlen=10)


current_word_global = ""


STABILITY_THRESHOLD = 10
stable_prediction = None
stable_counter = 0
last_accepted_gesture = None
last_area = 0
ALLOW_REPEAT_FACTOR = 1.30


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)



def _ensure_model_loaded():
    global _model, _X_train
    if _model is None:
        _model = joblib.load("modelo_gestos.pkl")

    if _X_train is None:
        try:
            _X_train = np.load("X_train.npy")
        except Exception:
            _X_train = None


def normalize_landmarks(hand_landmarks):
    x = np.array([lm.x for lm in hand_landmarks.landmark])
    y = np.array([lm.y for lm in hand_landmarks.landmark])
    z = np.array([lm.z for lm in hand_landmarks.landmark])
    x -= np.mean(x); y -= np.mean(y); z -= np.mean(z)
    scale = np.max([np.std(x), np.std(y), np.std(z)]) + 1e-8
    return np.concatenate([x/scale, y/scale, z/scale])


def classify_with_rejection(model, features, X_train=None,
                            conf_threshold=0.45,
                            dist_threshold=2.0):
    """
    Rejeita por baixa confiança; opcionalmente rejeita por distância se X_train for passado.
    """
    try:
        probs = model.predict_proba([features])[0]
    except Exception:
        
        pred = model.predict([features])[0]
        return pred

    best_prob = np.max(probs)
    best_label = model.classes_[np.argmax(probs)]

    if best_prob < conf_threshold:
        return None

    if X_train is not None:
        try:
            dist = pairwise_distances([features], X_train).min()
            if dist > dist_threshold:
                return None
        except Exception:
      
            pass

    return best_label



def release_camera():
    """Fecha a câmera (se aberta)."""
    global _cap
    try:
        if _cap is not None:
            _cap.release()
    except Exception:
        pass
    _cap = None


def reset_text():
    """Zera o texto exibido e limpa buffers/estado do reconhecimento."""
    global current_word_global, _buffer
    global stable_prediction, stable_counter, last_accepted_gesture, last_area

    current_word_global = ""
    _buffer.clear()
    stable_prediction = None
    stable_counter = 0
    last_accepted_gesture = None
    last_area = 0



def frame_generator():
    """
    Gera frames MJPEG. Abre a câmera apenas quando essa função é chamada.
    Mantém o texto atual em `current_word_global`.
    """
    global _cap, _model, _X_train
    global stable_prediction, stable_counter, last_accepted_gesture, last_area
    global current_word_global

    _ensure_model_loaded()

    if _cap is None:
        _cap = cv2.VideoCapture(0)

    while True:
        ret, frame = _cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture = ""
        hand_area = 0

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

             
                xs = [lm.x for lm in hand_landmarks.landmark]
                ys = [lm.y for lm in hand_landmarks.landmark]
                hand_area = (max(xs) - min(xs)) * (max(ys) - min(ys))

                landmarks = normalize_landmarks(hand_landmarks)

             
                pred = classify_with_rejection(_model, landmarks, _X_train)
                if pred is not None:
                    _buffer.append(pred)

            if _buffer:
              
                gesture = max(set(_buffer), key=_buffer.count)

       
        if gesture == stable_prediction:
            stable_counter += 1
        else:
            stable_prediction = gesture
            stable_counter = 1

   
        if stable_counter >= STABILITY_THRESHOLD:
            if stable_prediction not in ["", None, "SPACE", "DEL"]:
                allow_repeat = False
                if stable_prediction == last_accepted_gesture:
                    if hand_area > last_area * ALLOW_REPEAT_FACTOR:
                        allow_repeat = True
                else:
                    allow_repeat = True

                if allow_repeat:
                    current_word_global += stable_prediction
                    last_accepted_gesture = stable_prediction
                    last_area = hand_area
                    stable_counter = 0

            elif stable_prediction == "SPACE" and last_accepted_gesture != "SPACE":
                current_word_global += " "
                last_accepted_gesture = "SPACE"
                last_area = hand_area

            elif stable_prediction == "DEL" and last_accepted_gesture != "DEL" and len(current_word_global) > 0:
                current_word_global = current_word_global[:-1]
                last_accepted_gesture = "DEL"
                last_area = hand_area

            stable_counter = 0

   
        if gesture == "":
            last_accepted_gesture = None
            last_area = hand_area

     
        try:
            display_text = current_word_global
        except Exception:
            display_text = ""

        h, w, _ = frame.shape
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 2
        thickness = 3
        (tw, th), _ = cv2.getTextSize(display_text, font, scale, thickness)
        x = int((w - tw) / 2)
        y = int(h - 40)
        cv2.putText(frame, display_text, (x, y), font, scale, (255, 255, 255), thickness)

   
        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue
        frame_bytes = jpeg.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
