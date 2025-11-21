from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
import cv2
from recognition import process_frame, reset_text, get_current_text

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process_frame", methods=["POST"])
def process_frame_route():
    try:
        data = request.get_json()
        image_data = data["frame"]

        image_data = image_data.split(",")[1]
        img_bytes = base64.b64decode(image_data)

        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        gesture = process_frame(frame)
        text = get_current_text()

        return jsonify({"gesture": gesture, "text": text})

    except Exception as e:
        print("Erro:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/reset_text")
def reset_text_route():
    reset_text()
    return "ok"


@app.route("/1")
def pagina1():
    return render_template("pagina1.html")


@app.route("/2")
def pagina2():
    return render_template("pagina2.html")


@app.route("/3")
def pagina3():
    return render_template("pagina3.html")


@app.route("/trilha")
def trilha():
    return render_template("trilha.html")


@app.route("/trilha/1")
def trilha_modulo1():
    return render_template("modulo1.html")


@app.route("/trilha/2")
def trilha_modulo2():
    return render_template("modulo2.html")


@app.route("/trilha/3")
def trilha_modulo3():
    return render_template("modulo3.html")


@app.route("/trilha/certificado")
def certificado():
    usuario = "Usuário"
    return render_template("certificate.html", nome_usuario=usuario)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/maisTrilhas")
def maisTrilhas():
    return render_template("maisTrilhas.html")


if __name__ == "__main__":
    app.run(debug=True)
