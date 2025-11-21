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
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: "user" // câmera frontal
                },
                audio: false
            };
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
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

        fetch("/reset_text").then(() => recognizedDiv.textContent = "");
    };

    resetButton.onclick = function () {
        fetch("/reset_text")
            .then(res => res.json())
            .then(j => { recognizedDiv.textContent = j.text || ""; });
    };

    function initHands() {
        const hands = new Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
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
                if (!streaming) return;
                await hands.send({ image: videoElement });
                resizeCanvas();
            },
            width: 640,
            height: 480
        });

        videoElement.onloadedmetadata = function () {
            resizeCanvas();
            camera.start();
        };

        // Redimensionar canvas no resize da tela
        window.addEventListener("resize", resizeCanvas);
        setTimeout(resizeCanvas, 500); // fallback para celulares lentos
    }

    function resizeCanvas() {
        if (!videoElement.videoWidth || !videoElement.videoHeight) return;

        overlay.width = videoElement.videoWidth;
        overlay.height = videoElement.videoHeight;

        const rect = videoElement.getBoundingClientRect();
        overlay.style.width = rect.width + "px";
        overlay.style.height = rect.height + "px";
    }

    async function onResults(results) {
        const ctx = overlay.getContext("2d");
        ctx.clearRect(0, 0, overlay.width, overlay.height);

        if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) return;

        const lm = results.multiHandLandmarks[0];
        drawConnectors(ctx, lm, HAND_CONNECTIONS, { color: "#00FF00", lineWidth: 2 });
        drawLandmarks(ctx, lm, { color: "#FF0000", lineWidth: 1 });

        const flat = lm.flatMap(p => [p.x, p.y, p.z ?? 0]);
        const xs = lm.map(p => p.x);
        const ys = lm.map(p => p.y);
        const hand_area = (Math.max(...xs) - Math.min(...xs)) * (Math.max(...ys) - Math.min(...ys));

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
            if (j.text !== undefined) recognizedDiv.textContent = j.text;
        } catch (err) {
            console.error("Erro ao enviar landmarks:", err);
        }
    }

});
