const API_URL = "https://YOUR_NETLIFY_URL.netlify.app/.netlify/functions/chatbot";

let messages = [];

function addMessage(text, sender = "bot") {
    const container = document.createElement("div");
    container.className = "message " + sender;
    container.innerText = text;
    document.getElementById("chat-messages").appendChild(container);
    document.getElementById("chat-messages").scrollTop = 999999;
}

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    const payload = {
        message: text,
        messages: messages
    };

    const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    const botMsg = data.response || "Error";
    messages = data.messages;

    addMessage(botMsg, "bot");
}

// UI events
document.getElementById("chat-send").onclick = sendMessage;
document.getElementById("chat-input").addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});

document.getElementById("chat-button").onclick = () => {
    document.getElementById("chat-window").classList.remove("hidden");
};

document.getElementById("chat-close").onclick = () => {
    document.getElementById("chat-window").classList.add("hidden");
};
