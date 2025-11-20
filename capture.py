import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os
import sys

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

label = 'DEL'
if len(sys.argv) > 1:
    label = sys.argv[1]

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

print(f"[INFO] Capturando dados para o gesto '{label}'. Pressione 'r' para encerrar e salvar, ou 'q' para sair sem salvar.")

data = []
texto = "" 

def normalize_landmarks(hand_landmarks):
    x = np.array([lm.x for lm in hand_landmarks.landmark])
    y = np.array([lm.y for lm in hand_landmarks.landmark])
    z = np.array([lm.z for lm in hand_landmarks.landmark])
    x -= np.mean(x); y -= np.mean(y); z -= np.mean(z)
    scale = np.max([np.std(x), np.std(y), np.std(z)]) + 1e-8
    return np.concatenate([x/scale, y/scale, z/scale])

while True:
    ret, frame = cap.read()
    if not ret:
        print('[ERRO] Não foi possível acessar a câmera.')
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

  
    if label.upper() == "SPACE":
        texto += " "
    elif label.upper() == "DEL":
        texto = texto[:-1] 
    else:
        texto += label  

   
    cv2.putText(frame, texto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = normalize_landmarks(hand_landmarks)
            data.append(landmarks)

    cv2.imshow('Captura de Gesto', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        break
    if key == ord('q'):
        data = []
        break

cap.release()
cv2.destroyAllWindows()

if data:
    df = pd.DataFrame(data)
    df['label'] = label
    file_path = os.path.join(DATA_DIR, f"gesto_{label}.csv")
    df.to_csv(file_path, index=False)
    print(f"[OK] Dados salvos em: {file_path}")
else:
    print('[AVISO] Nenhum dado capturado — nada foi salvo.')
