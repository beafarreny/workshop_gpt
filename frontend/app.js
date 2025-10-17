const API = (localStorage.API || "http://127.0.0.1:8000").replace(/\/$/, "");
const USER = localStorage.USER || "demo-user";

const historyEl = document.getElementById("history");
const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const providerEl = document.getElementById("provider");

async function health() {
  try {
    const res = await fetch(`${API}/health`);
    const data = await res.json();
    providerEl.textContent = `Modelo: ${data.provider}`;
  } catch (e) {
    providerEl.textContent = "Sin conexión al backend";
  }
}

async function loadHistory() {
  const res = await fetch(`${API}/chat-system/chat/${USER}`);
  const data = await res.json();
  historyEl.innerHTML = "";
  data.forEach(msg => appendMsg(msg));
}

function appendMsg({ role, content }) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = `${role === "assistant" ? "🤖" : "🧑"} ${content}`;
  historyEl.appendChild(div);
  historyEl.scrollTop = historyEl.scrollHeight;
}

async function sendMessage(text) {
  await fetch(`${API}/chat-system/chat/${USER}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: text })
  });
  appendMsg({ role: "user", content: text });

  const res = await fetch(`${API}/chat-system/chat-streaming/${USER}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: text })
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let aiChunk = "";
  let aiDiv = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    aiChunk += decoder.decode(value, { stream: true });
    if (!aiDiv) {
      aiDiv = document.createElement("div");
      aiDiv.className = "message assistant";
      historyEl.appendChild(aiDiv);
    }
    aiDiv.textContent = `🤖 ${aiChunk}`;
    historyEl.scrollTop = historyEl.scrollHeight;
  }
}

form.addEventListener("submit", e => {
  e.preventDefault();
  const text = input.value.trim();
  if (text) {
    sendMessage(text);
    input.value = "";
  }
});

await health();
await loadHistory();
