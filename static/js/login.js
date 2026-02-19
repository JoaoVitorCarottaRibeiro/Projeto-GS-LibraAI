document.addEventListener("DOMContentLoaded", () => {

    const loginBtn = document.getElementById("loginBtn");
    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");

    if (!loginBtn) return;

    async function handleLogin() {

        const email = emailInput.value.trim();
        const senha = senhaInput.value.trim();

        if (!email || !senha) {
            alert("Preencha email e senha");
            return;
        }

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, senha })
            });

            const result = await response.json();

            if (result.success) {
                window.location.href = "/home";
            } else {
                alert(result.message || "Email ou senha inválidos");
            }

        } catch (err) {
            console.error(err);
            alert("Erro ao conectar com o servidor");
        }
    }

    loginBtn.addEventListener("click", handleLogin);

    
    [emailInput, senhaInput].forEach(input => {
        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                handleLogin();
            }
        });
    });

});
