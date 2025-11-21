let streaming = false;
let cameraStream = null;

document.getElementById("startButton").onclick = async function () {
    const container = document.getElementById("videoContainer");
    const video = document.getElementById("userCamera");
    const output = document.getElementById("recognizedText");

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = cameraStream;
        container.style.display = "block";
        this.style.display = "none";
        streaming = true;

        sendFrames();
    } catch (err) {
        alert("Erro ao acessar a câmera: " + err);
    }
};


document.getElementById("closeButton").onclick = function () {
    streaming = false;

    if (cameraStream) {
        cameraStream.getTracks().forEach(t => t.stop());
    }

    document.getElementById("videoContainer").style.display = "none";
    document.getElementById("startButton").style.display = "inline";

    fetch("/reset_text");
};


async function sendFrames() {
    const video = document.getElementById("userCamera");
    const canvas = document.createElement("canvas");

    const output = document.getElementById("recognizedText");

    while (streaming) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        let ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        let dataURL = canvas.toDataURL("image/jpeg");

        let response = await fetch("/process_frame", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ frame: dataURL })
        });

        let result = await response.json();
        if (result.text !== undefined) {
            output.textContent = result.text;
        }

        await new Promise(r => setTimeout(r, 200)); // 5 FPS
    }
}
