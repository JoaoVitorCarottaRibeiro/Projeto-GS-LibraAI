document.getElementById("loginBtn").addEventListener("click", () => {
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value.trim();

    if (!email || !senha) {
        alert("Preencha email e senha.");
        return;
    }

    alert("Login realizado (simulado).");

    window.location.href = "/dashboard"; 
});



