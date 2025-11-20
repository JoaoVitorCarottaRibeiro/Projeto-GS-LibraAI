document.getElementById('startButton').onclick = function () {
    const video = document.getElementById('video');
    const container = document.getElementById('videoContainer');

    video.src = '/video_feed';
    container.style.display = 'block';

    this.style.display = 'none';
};

// Fechar câmera e resetar IA
document.getElementById('closeButton').onclick = function () {
    const video = document.getElementById('video');
    const container = document.getElementById('videoContainer');

    video.src = '';
    container.style.display = 'none';

    document.getElementById('startButton').style.display = 'inline';

    fetch('/stop_camera');
    fetch('/reset_text');
};

// Leitura do progresso salvo
let progress = localStorage.getItem("trackProgress") || 0;

// Atualiza barra nos módulos e na trilha
document.addEventListener("DOMContentLoaded", () => {
    const fill = document.querySelector(".progress-fill");
    if (fill) fill.style.width = progress + "%";
});

// Avança módulo
function goNextModule(next) {
    if (next === 2) updateProgress(33);
    if (next === 3) updateProgress(66);
    window.location.href = `/trilha/${next}`;
}

// Finaliza trilha
function finishTrack() {
    updateProgress(100);
    window.location.href = "/trilha/certificado";
}

function updateProgress(value) {
    localStorage.setItem("trackProgress", value);
}


function downloadCertificate() {
    alert("Função de download pode ser integrada com html2canvas ou conversão em PDF.");
}

function submitQuiz(module) {
    const form = document.getElementById(`quiz${module}`);
    const feedback = document.getElementById("quiz-feedback");

    const answers = {
        1: ["b", "c", "a"],
        2: ["b", "b", "a"],
        3: ["b", "b", "a"]
    };

    const userAnswers = [
        form.q1.value,
        form.q2.value,
        form.q3.value
    ];

    if (userAnswers.includes("")) {
        feedback.style.color = "red";
        feedback.textContent = "Responda todas as perguntas!";
        return;
    }

    const correct = userAnswers.every((ans, i) => ans === answers[module][i]);

    if (!correct) {
        feedback.style.color = "red";
        feedback.textContent = "Você errou! Revise o conteúdo e tente novamente.";
        return;
    }

    feedback.style.color = "green";
    feedback.textContent = "Parabéns! Você acertou tudo!";

    if (module === 1) {
        localStorage.setItem("trackProgress", 33);
        setTimeout(() => window.location.href = "/trilha/2", 1500);
    }
    if (module === 2) {
        localStorage.setItem("trackProgress", 66);
        setTimeout(() => window.location.href = "/trilha/3", 1500);
    }
    if (module === 3) {
        localStorage.setItem("trackProgress", 100);
        setTimeout(() => window.location.href = "/trilha/certificado", 1500);
    }
}


