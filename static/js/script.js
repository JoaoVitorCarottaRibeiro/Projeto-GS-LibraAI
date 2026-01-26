document.addEventListener("DOMContentLoaded", function () {

    let camera = null;
    let streaming = false;
    let sendIntervalMs = 200;
    let lastSent = 0;

    const startButton = document.getElementById("startButton");
    const closeButton = document.getElementById("closeButton");
    const resetButton = document.getElementById("resetButton");
    const videoElement = document.getElementById("userCamera");
    const overlay = document.getElementById("overlay");
    const recognizedDiv = document.getElementById("recognizedText");

    
    startButton.onclick = async function () {
        const container = document.getElementById("videoContainer");

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoElement.srcObject = stream;

            container.style.display = "block";
            startButton.style.display = "none";
            streaming = true;

            initHands();
        } catch (err) {
            alert("Erro ao acessar a câmera: " + err);
        }
    };

    
    closeButton.onclick = function () {
        streaming = false;

        const stream = videoElement.srcObject;
        if (stream) stream.getTracks().forEach(t => t.stop());

        document.getElementById("videoContainer").style.display = "none";
        startButton.style.display = "inline";

        fetch("/reset_text").then(() => {
            recognizedDiv.textContent = "";
        });
    };

    
    resetButton.onclick = function () {
        fetch("/reset_text")
            .then(res => res.json())
            .then(j => { recognizedDiv.textContent = j.text || ""; });
    };

    
    function initHands() {
        const hands = new Hands({
            locateFile: (file) =>
                `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        });

        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.6,
            minTrackingConfidence: 0.6
        });

        hands.onResults(onResults);

        camera = new Camera(videoElement, {
            onFrame: async () => {
                await hands.send({ image: videoElement });
                resizeCanvas();
            }
        });

        videoElement.onloadedmetadata = function () {
            resizeCanvas();
            camera.start();
        };

        window.addEventListener("resize", resizeCanvas);
    }

    
    function resizeCanvas() {
        const video = videoElement;
        const canvas = overlay;

        if (!video.videoWidth || !video.videoHeight) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const rect = video.getBoundingClientRect();
        canvas.style.width = rect.width + "px";
        canvas.style.height = rect.height + "px";
    }

    
    async function onResults(results) {
        const canvas = overlay;
        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
            return;
        }

        const lm = results.multiHandLandmarks[0];

        drawConnectors(ctx, lm, HAND_CONNECTIONS, { color: "#00FF00", lineWidth: 2 });
        drawLandmarks(ctx, lm, { color: "#FF0000", lineWidth: 1 });

        const flat = lm.flatMap(p => [p.x, p.y, p.z ?? 0]);

        const xs = lm.map(p => p.x);
        const ys = lm.map(p => p.y);
        const hand_area =
            (Math.max(...xs) - Math.min(...xs)) *
            (Math.max(...ys) - Math.min(...ys));

        const now = Date.now();

        if (now - lastSent < sendIntervalMs) return;
        lastSent = now;

        try {
            const resp = await fetch("/classify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ landmarks: flat, hand_area })
            });

            const j = await resp.json();
            if (j.text !== undefined) {
                recognizedDiv.textContent = j.text;
            }

        } catch (err) {
            console.error("Erro ao enviar landmarks:", err);
        }
    }

});

// JS Módulos e barra de progresso //

const quizAnswers = {
    1: { q1: "b", q2: "c", q3: "a" },
    2: { q1: "b", q2: "b", q3: "a" },
    3: { q1: "b", q2: "b", q3: "a" }
};

function submitQuiz(moduleNumber) {
    const form = document.getElementById(`quiz${moduleNumber}`);
    const feedback = document.getElementById("quiz-feedback");

    let correct = 0;
    const answers = quizAnswers[moduleNumber];

    for (let q in answers) {
        const selected = form.querySelector(`input[name="${q}"]:checked`);
        if (!selected) {
            feedback.textContent = "⚠️ Responda todas as perguntas.";
            feedback.style.color = "orange";
            return;
        }
        if (selected.value === answers[q]) {
            correct++;
        }
    }

    if (correct === 3) {
        markModuleCompleted(moduleNumber);
        feedback.textContent = "✅ Parabéns! Você concluiu este módulo.";
        feedback.style.color = "green";

        setTimeout(() => {
            if (moduleNumber < 3) {
                window.location.href = `/trilha/${moduleNumber + 1}`;
            } else {
                window.location.href = "/trilha/certificado";
            }
        }, 1500);

    } else {
        feedback.textContent = "❌ Algumas respostas estão incorretas. Tente novamente.";
        feedback.style.color = "red";
    }
}

// ===============================
// PROGRESSO DA TRILHA
// ===============================

function markModuleCompleted(moduleNumber) {
    let progress = JSON.parse(localStorage.getItem("trilhaProgress")) || [];
    if (!progress.includes(moduleNumber)) {
        progress.push(moduleNumber);
        localStorage.setItem("trilhaProgress", JSON.stringify(progress));
    }
}

function updateProgressBar() {
    const progress = JSON.parse(localStorage.getItem("trilhaProgress")) || [];
    const percent = (progress.length / 3) * 100;

    const bar = document.querySelector(".progress-fill");
    if (bar) {
        bar.style.width = percent + "%";
    }
}

document.addEventListener("DOMContentLoaded", updateProgressBar);
