from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for
)
import sqlite3
import hashlib
import os
import time
import numpy as np
import recognition
from werkzeug.utils import secure_filename

from database import (
    create_tables,
    get_connection,
    get_user_by_email,
    update_module_progress,
    init_user_points,
    add_points_to_user,
    get_top_3_users,
    get_top_10_users
)

# CONFIG

app = Flask(__name__)
app.secret_key = "librAI_super_secret_key"

create_tables()

TOTAL_MODULES = 3

MODULE_POINTS = {
    1: 100,
    2: 50,
    3: 150
}

# HELPERS

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT module_id, status
        FROM user_progress
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return {row["module_id"]: row["status"] for row in rows}


def normalize_progress(progress_map):
    """
    USAR APENAS PARA UI
    """
    normalized = {}
    for module_id in range(1, TOTAL_MODULES + 1):
        normalized[module_id] = progress_map.get(module_id, "not_started")
    return normalized


def calculate_progress_percent(user_id):
    """
    FONTE DA VERDADE = BANCO
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM user_progress
        WHERE user_id = ?
        AND status = 'completed'
    """, (user_id,))

    completed = cursor.fetchone()[0]
    conn.close()

    return int((completed / TOTAL_MODULES) * 100)


def normalize_landmarks_from_array(arr):
    arr = np.array(arr)
    x = arr[0::3]
    y = arr[1::3]
    z = arr[2::3]

    x -= np.mean(x)
    y -= np.mean(y)
    z -= np.mean(z)

    scale = max(np.std(x), np.std(y), np.std(z), 1e-8)
    return np.concatenate([x/scale, y/scale, z/scale])

# ROTAS BÁSICAS

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/1")
def conectando_pessoas():
    return render_template("pagina1.html")

@app.route("/2")
def ampliando_oportunidades():
    return render_template("pagina2.html")

@app.route("/3")
def tecnologia_com_proposito():
    return render_template("pagina3.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# AUTH

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.json

    nome = data.get("nome")
    idade = data.get("idade")
    profissao = data.get("profissao")
    email = data.get("email")
    senha = data.get("senha")

    if not all([nome, idade, profissao, email, senha]):
        return jsonify({"error": "Dados incompletos"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (nome, idade, profissao, email, senha)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, idade, profissao, email, hash_password(senha)))

        user_id = cursor.lastrowid
        conn.commit()

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email já cadastrado"}), 409
    finally:
        conn.close()

    init_user_points(user_id)
    return jsonify({"success": True})


@app.route("/login", methods=["POST"])
def login_post():
    data = request.get_json()

    email = data.get("email")
    senha = data.get("senha")

    user = get_user_by_email(email)

    if not user or user["senha"] != hash_password(senha):
        return jsonify({"success": False})

    session["user_id"] = user["id"]
    session["user_name"] = user["nome"]

    return jsonify({"success": True})

# HOME

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    raw_progress = get_user_progress(session["user_id"])
    progress_map = normalize_progress(raw_progress)
    progress_percent = calculate_progress_percent(session["user_id"])
    top3 = get_top_3_users()

    all_completed = progress_percent == 100

    return render_template(
        "home.html",
        progress_map=progress_map,
        progress_percent=progress_percent,
        top3=top3,
        all_completed=all_completed
    )

# TRILHAS

@app.route("/trilha/<int:module_id>")
def trilha_modulo(module_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    progress_map = get_user_progress(session["user_id"])
    status = progress_map.get(module_id)

    if status is None:
        update_module_progress(
            session["user_id"],
            module_id,
            "in_progress"
        )

    return render_template(f"modulo{module_id}.html")

@app.route("/trilha/<int:module_id>/concluir", methods=["POST"])
def concluir_modulo(module_id):
    if "user_id" not in session:
        return jsonify({"error": "Não autenticado"}), 401

    user_id = session["user_id"]
    progress_map = get_user_progress(user_id)

    if progress_map.get(module_id) != "completed":
        update_module_progress(user_id, module_id, "completed")
        add_points_to_user(user_id, MODULE_POINTS.get(module_id, 0))

    return jsonify({"success": True})

@app.route("/upload-foto", methods=["POST"])
def upload_foto():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if "photo" not in request.files:
        return redirect(url_for("home"))

    photo = request.files["photo"]
    if photo.filename == "":
        return redirect(url_for("home"))

    filename = secure_filename(photo.filename)
    path = os.path.join("static/uploads", filename)
    photo.save(path)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET foto_perfil = ? WHERE id = ?",
        (path, session["user_id"])
    )
    conn.commit()
    conn.close()

    session["user_photo"] = path
    return redirect(url_for("home"))

@app.route("/ranking")
def ranking():
    if "user_id" not in session:
        return redirect(url_for("login"))

    users = get_top_10_users()
    return render_template("ranking.html", ranking=users)

@app.route("/certificados")
def certificados():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    progress_percent = calculate_progress_percent(user_id)

    if progress_percent < 100:
        return redirect(url_for("home"))

    return render_template(
        "certificados.html",
        nome_usuario=session["user_name"]
    )

@app.route("/certificate")
def certificate():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    progress_percent = calculate_progress_percent(user_id)

    if progress_percent < 100:
        return redirect(url_for("home"))

    return render_template(
        "certificate.html",
        nome_usuario=session["user_name"]
    )

@app.route("/maisTrilhas")
def mais_trilhas():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("maisTrilhas.html")

# IA

@app.route("/classify", methods=["POST"])
def classify():
    data = request.json
    landmarks = data.get("landmarks")

    if not landmarks:
        return jsonify({"text": recognition.get_current_text()})

    features = normalize_landmarks_from_array(landmarks)

    recognition._ensure_model_loaded()

    gesture = recognition.classify(recognition._model, features)

    if gesture:
        now = time.time()
        if gesture != recognition._last_added or (now - recognition._last_time) > recognition.COOLDOWN:
            if gesture == "SPACE":
                recognition.current_text += " "
            elif gesture == "DEL":
                recognition.current_text = recognition.current_text[:-1]
            else:
                recognition.current_text += gesture
            recognition._last_added = gesture
            recognition._last_time = now
    return jsonify({"text": recognition.get_current_text()})


@app.route("/reset_text")
def reset_text():
    recognition.reset_text()
    return jsonify({"text": ""})

if __name__ == "__main__":
    app.run(debug=True)
