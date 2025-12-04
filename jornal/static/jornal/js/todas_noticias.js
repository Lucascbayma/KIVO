const input = document.getElementById("campo-busca");
const box = document.getElementById("caixa-sugestoes");

input.addEventListener("input", async () => {
    const termo = input.value.trim();

    if (termo.length < 2) {
        box.classList.add("hidden");
        return;
    }

    const resp = await fetch(`/api/sugestoes/?q=${encodeURIComponent(termo)}`);
    const sugestoes = await resp.json();

    if (sugestoes.length === 0) {
        box.classList.add("hidden");
        return;
    }

    box.innerHTML = "";
    sugestoes.forEach(txt => {
        const div = document.createElement("div");
        div.textContent = txt;
        div.classList.add("sugestoes-item");

        div.onclick = () => {
            input.value = txt;
            box.classList.add("hidden");
        };

        box.appendChild(div);
    });

    box.classList.remove("hidden");
});

document.addEventListener("click", (e) => {
    if (!input.contains(e.target)) {
        box.classList.add("hidden");
    }
});
