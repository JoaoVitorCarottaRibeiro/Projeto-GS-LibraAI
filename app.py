from flask import Flask, Response, render_template
from recognition import frame_generator, release_camera, reset_text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(frame_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    release_camera()
    return "camera stopped"

@app.route('/reset_text')
def reset_text_route():
    reset_text()
    return "text reset"

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
