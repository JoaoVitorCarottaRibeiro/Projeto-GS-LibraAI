document.getElementById("signupBtn").addEventListener("click", async () => {
    const payload = {
        nome: document.getElementById("nome").value,
        idade: document.getElementById("idade").value,
        profissao: document.getElementById("profissao").value,
        email: document.getElementById("email").value,
        senha: document.getElementById("senha").value
    };

    const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (data.success) {
        alert("Conta criada com sucesso!");
        window.location.href = "/login";
    } else {
        alert(data.error || "Erro ao cadastrar");
    }
});
