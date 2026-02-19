import cv2
import joblib
import numpy as np
import mediapipe as mp
from collections import deque

_model = None
_X_train = None
current_text = ""

_buffer = deque(maxlen=8)

_last_added = None
_last_time = 0
COOLDOWN = 2.0


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

    x -= np.mean(x)
    y -= np.mean(y)
    z -= np.mean(z)

    scale = np.max([np.std(x), np.std(y), np.std(z)]) + 1e-8
    return np.concatenate([x / scale, y / scale, z / scale])


def classify(model, features):
    probs = model.predict_proba([features])[0]
    best_prob = np.max(probs)

    if best_prob < 0.45:
        return None

    return model.classes_[np.argmax(probs)]


def process_frame(frame):
    global current_text

    _ensure_model_loaded()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if not result.multi_hand_landmarks:
        return None

    gesture = None

    for hand_landmarks in result.multi_hand_landmarks:
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        landmarks = normalize_landmarks(hand_landmarks)
        gesture = classify(_model, landmarks)

    if gesture:
        _buffer.append(gesture)
        most = max(set(_buffer), key=_buffer.count)

        if most == "SPACE":
            current_text += " "
        elif most == "DEL":
            current_text = current_text[:-1]
        else:
            current_text += most

        return most

    return None


def reset_text():
    global current_text
    current_text = ""


def get_current_text():
    return current_text
