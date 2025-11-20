document.getElementById("signupBtn").addEventListener("click", () => {
    const data = {
        nome: document.getElementById("nome").value.trim(),
        idade: document.getElementById("idade").value.trim(),
        profissao: document.getElementById("profissao").value.trim(),
        email: document.getElementById("email").value.trim(),
        senha: document.getElementById("senha").value.trim()
    };

    if (!data.nome || !data.email || !data.senha) {
        alert("Preencha ao menos nome, email e senha.");
        return;
    }

    alert("Cadastro realizado (simulado).");
    window.location.href = "/login";
});
