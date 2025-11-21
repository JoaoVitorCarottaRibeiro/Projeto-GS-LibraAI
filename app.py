# app.py
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from collections import deque
from sklearn.metrics import pairwise_distances

app = Flask(__name__)

# --------------------
# Modelo / estado
# --------------------
_model = None
_X_train = None

# recognition state
_buffer = deque(maxlen=8)
STABILITY_THRESHOLD = 6
stable_prediction = None
stable_counter = 0
last_accepted_gesture = None
last_area = 0.0
ALLOW_REPEAT_FACTOR = 1.30

current_text = ""

# --------------------
# Helpers
# --------------------
def _ensure_model_loaded():
    global _model, _X_train
    if _model is None:
        _model = joblib.load("modelo_gestos.pkl")  # ajuste se necessário
    if _X_train is None:
        try:
            _X_train = np.load("X_train.npy")
        except Exception:
            _X_train = None

def classify_with_rejection(model, features, X_train=None,
                            conf_threshold=0.45,
                            dist_threshold=2.0):
    """
    retorna label ou None (rejeitado)
    """
    try:
        probs = model.predict_proba([features])[0]
        best_prob = np.max(probs)
        best_label = model.classes_[np.argmax(probs)]
    except Exception:
        # fallback para modelos que não suportam predict_proba
        best_label = model.predict([features])[0]
        return best_label

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

def normalize_landmarks_list(landmarks):
    """
    landmarks: flat list [x0,y0,z0, x1,y1,z1, ...] or list of {x,y,z}
    We expect a flat list of 63 floats (21*3) coming from client already,
    but just in case, handle either format.
    This function returns normalized numpy 1D array length 63.
    """
    arr = np.array(landmarks, dtype=float).reshape(-1, 3)
    x = arr[:,0].copy()
    y = arr[:,1].copy()
    z = arr[:,2].copy()
    x -= x.mean(); y -= y.mean(); z -= z.mean()
    scale = max(np.std(x), np.std(y), np.std(z), 1e-8)
    norm = np.concatenate([x/scale, y/scale, z/scale])
    return norm

# --------------------
# Routes
# --------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/classify", methods=["POST"])
def classify_route():
    """
    Recebe JSON:
    {
      "landmarks": [x0,y0,z0, x1,y1,z1, ...]  (21*3 = 63 items)
      "hand_area": float  (opcional, usado para permitir repeats)
    }
    Retorna JSON:
    {
      "gesture": "<label or null>",
      "accepted": true/false,   # se foi aceito e aplicado ao texto
      "text": "<current_text>"
    }
    """
    global _buffer, stable_prediction, stable_counter, last_accepted_gesture, last_area, current_text
    try:
        data = request.get_json()
        landmarks = data.get("landmarks")
        hand_area = float(data.get("hand_area", 0.0))

        if landmarks is None:
            return jsonify({"error": "missing landmarks"}), 400

        _ensure_model_loaded()
        feats = normalize_landmarks_list(landmarks)

        pred = classify_with_rejection(_model, feats, _X_train)

        gesture = None
        accepted = False

        if pred is not None:
            _buffer.append(pred)
            # majority vote in buffer
            gesture = max(set(_buffer), key=_buffer.count)
        else:
            # no detection -> clear buffer
            _buffer.clear()
            gesture = ""

        # stability logic (similar to seu código anterior)
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
                    current_text += stable_prediction
                    last_accepted_gesture = stable_prediction
                    last_area = hand_area
                    accepted = True

            elif stable_prediction == "SPACE" and last_accepted_gesture != "SPACE":
                current_text += " "
                last_accepted_gesture = "SPACE"
                last_area = hand_area
                accepted = True

            elif stable_prediction == "DEL" and last_accepted_gesture != "DEL" and len(current_text) > 0:
                current_text = current_text[:-1]
                last_accepted_gesture = "DEL"
                last_area = hand_area
                accepted = True

            stable_counter = 0

        # if no gesture detected, reset last_accepted to allow next acceptance when hand returns
        if gesture == "":
            last_accepted_gesture = None
            last_area = hand_area

        return jsonify({"gesture": gesture if gesture != "" else None,
                        "accepted": bool(accepted),
                        "text": current_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset_text", methods=["GET"])
def reset_text_route():
    global current_text, _buffer, stable_prediction, stable_counter, last_accepted_gesture, last_area
    current_text = ""
    _buffer.clear()
    stable_prediction = None
    stable_counter = 0
    last_accepted_gesture = None
    last_area = 0.0
    return jsonify({"ok": True, "text": current_text})


# (opcionais: páginas existentes no seu projeto)
@app.route("/1")
def pagina1(): return render_template("pagina1.html")
@app.route("/2")
def pagina2(): return render_template("pagina2.html")
@app.route("/3")
def pagina3(): return render_template("pagina3.html")
@app.route("/trilha")
def trilha(): return render_template("trilha.html")
@app.route("/trilha/1")
def trilha_modulo1(): return render_template("modulo1.html")
@app.route("/trilha/2")
def trilha_modulo2(): return render_template("modulo2.html")
@app.route("/trilha/3")
def trilha_modulo3(): return render_template("modulo3.html")
@app.route("/trilha/certificado")
def certificado():
    usuario = "Usuário"
    return render_template("certificate.html", nome_usuario=usuario)
@app.route("/login")
def login(): return render_template("login.html")
@app.route("/signup")
def signup(): return render_template("signup.html")
@app.route("/maisTrilhas")
def maisTrilhas(): return render_template("maisTrilhas.html")

# --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
