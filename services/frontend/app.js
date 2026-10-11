const form = document.querySelector("#item-form");
const input = document.querySelector("#name");
const button = document.querySelector("#submit");
const message = document.querySelector("#message");
const list = document.querySelector("#items");

async function loadItems() {
  const response = await fetch("/api/items");
  if (!response.ok) {
    throw new Error("Impossible de charger les éléments.");
  }

  const data = await response.json();
  list.replaceChildren();

  for (const item of data.items) {
    const li = document.createElement("li");
    li.textContent = `${item.id} — ${item.name}`;
    list.appendChild(li);
  }

  if (data.items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Aucun élément pour le moment.";
    list.appendChild(li);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  button.disabled = true;
  message.textContent = "";

  try {
    const response = await fetch("/api/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: input.value })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Échec de l'ajout.");
    }

    input.value = "";
    message.textContent = "Élément enregistré.";
    await loadItems();
  } catch (error) {
    message.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

loadItems().catch((error) => {
  message.textContent = error.message;
});
