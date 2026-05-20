(() => {
  console.log("🚀 Loaded Suraj AI Floating Widget");

  const CONFIG = window.__CHAT_WIDGET_CONFIG__ || {};
  const API_URL = CONFIG.apiUrl || "https://multi-agent-ai-chatbot.onrender.com/chat";
  const BOT_NAME = CONFIG.name || "AI Student Assistant";
  const SCHOOL_SUBTITLE = CONFIG.subtitle || "Career Training School";
  const BOT_LOGO = CONFIG.logo || "./avatar.png";

  const notificationSound = new Audio(CONFIG.sound || "./notify.mp3");
  notificationSound.volume = 0.6;

  /* ---------------- FORMATTER (FIXED) ---------------- */
  function formatBotMessage(text, role) {
    if (!text) return "";

    // Convert URLs → clickable links
    text = text.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank">$1</a>'
    );

    // Convert bullet points → list
    if (text.includes("•") || text.includes("- ")) {
      const lines = text.split("\n").filter(l => l.trim() !== "");

      const listItems = lines.map(line => {
        return `<li>${line.replace(/^•|- /, "").trim()}</li>`;
      }).join("");

      return `<ul style="padding-left:18px; margin:8px 0;">${listItems}</ul>`;
    }

    // Line breaks
    text = text.replace(/\n/g, "<br>");

    return text;
  }

  let sessionId = null;

  function generateSessionId() {
    return "web-" + crypto.randomUUID();
  }

  function resetSession() {
    sessionId = generateSessionId();
  }

  /* ---------------- CHATBOX ---------------- */

  const chatbox = document.createElement("div");
  chatbox.className = "suraj-chatbox";

  chatbox.innerHTML = `
    <div class="suraj-header">
      <img src="${BOT_LOGO}">
      <div>
        <div class="suraj-header-title">${BOT_NAME}</div>
        <div class="suraj-header-sub">${SCHOOL_SUBTITLE}</div>
      </div>
      <div class="suraj-refresh" id="surajRefresh">⟳</div>
      <div class="suraj-close" id="surajClose">×</div>
    </div>

    <div class="suraj-messages" id="surajMsgs"></div>

    <div class="suraj-input">
      <input id="surajInput" placeholder="Write a message...">
      <button id="surajSend" type="button">Send</button>
    </div>
  `;

  document.body.appendChild(chatbox);

  const msgs = document.getElementById("surajMsgs");
  const input = document.getElementById("surajInput");

  let typingEl = null;

  function showTyping() {
    if (typingEl) return;
    typingEl = document.createElement("div");
    typingEl.className = "typing";
    typingEl.innerHTML = `<span></span><span></span><span></span>`;
    msgs.appendChild(typingEl);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function hideTyping() {
    if (typingEl) typingEl.remove();
    typingEl = null;
  }

  function lockInput(lock = true) {
    input.disabled = lock;
  }

  /* ---------------- RENDER ---------------- */

  function addBotMessage(text) {
    const el = document.createElement("div");
    el.className = "suraj-bot suraj-message";

    const formatted = formatBotMessage(text, "bot");
    el.innerHTML = formatted;

    el.querySelectorAll("a").forEach(link => {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    });

    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
    notificationSound.play().catch(() => {});
  }

  function addUserMessage(text) {
    const el = document.createElement("div");
    el.className = "suraj-user";
    el.innerText = text;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function addBotButtons(buttons) {
    lockInput(true);

    const wrap = document.createElement("div");
    wrap.className = "suraj-buttons";

    buttons.forEach(btn => {
      const b = document.createElement("button");
      b.className = "suraj-btn";
      b.innerText = btn.label;

      b.onclick = () => {
        lockInput(false);

        if (btn.value === "__ask_free_text__") {
          input.focus();
          return;
        }

        sendMessage(btn.value);
      };

      wrap.appendChild(b);
    });

    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function addProgramDropdown(options) {
    lockInput(true);

    const wrap = document.createElement("div");
    wrap.className = "suraj-dropdown";

    const select = document.createElement("select");
    select.innerHTML = `<option value="">🎓 Select program</option>`;

    options.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p;
      opt.innerText = p;
      select.appendChild(opt);
    });

    select.onchange = () => {
      if (select.value) {
        lockInput(false);
        sendMessage(select.value);
      }
    };

    wrap.appendChild(select);
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
  }

  /* ---------------- API ---------------- */

  async function sendMessage(message) {
    if (!message) return;

    addUserMessage(message);
    showTyping();

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message
        })
      });

      const data = await res.json();
      hideTyping();
      handleBotReply(data.reply, data.meta);

    } catch (e) {
      hideTyping();
      addBotMessage("⚠️ Something went wrong.");
      lockInput(false);
    }
  }

  function handleBotReply(reply, meta) {
    addBotMessage(reply);

    if (!meta) {
      lockInput(false);
      return;
    }

    switch (meta.type) {
      case "program_dropdown":
        addProgramDropdown(meta.options);
        break;
      case "confirm_buttons":
        addBotButtons(meta.buttons);
        break;
      default:
        lockInput(false);
    }
  }

  /* ---------------- LAUNCHER ---------------- */

  const launcher = document.createElement("div");
  launcher.className = "suraj-launcher";

  launcher.innerHTML = `
    <div class="suraj-label">Chat With Us</div>
    <div class="suraj-circle">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="#1e3a8a">
        <path d="M21 15a4 4 0 0 1-4 4H7l-4 4V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/>
      </svg>
    </div>
  `;

  document.body.appendChild(launcher);

  launcher.onclick = () => {
    window.toggleChatWidget();
  };

  /* ---------------- CONTROL ---------------- */

  window.toggleChatWidget = function () {
    const isOpen = chatbox.style.display === "flex";

    if (isOpen) {
      chatbox.style.display = "none";
    } else {
      chatbox.style.display = "flex";
      if (!sessionId) resetSession();
      msgs.innerHTML = "";
      addBotMessage("👋 Hello! How can I assist you today?");
      addBotButtons([
        { label: "🏛️ About Us", value: "about us" },
        { label: "📚 Programs", value: "programs" },
        { label: "💰 Financial Aid", value: "financial aid" },
        { label: "📅 Make an Appointment", value: "book appointment" },
        { label: "❓ Ask a Question", value: "__ask_free_text__" }
      ]);
    }
  };

  document.getElementById("surajClose").onclick = () => {
    chatbox.style.display = "none";
  };

  document.getElementById("surajRefresh").onclick = () => {
    sessionId = null;
    window.toggleChatWidget();
  };

  document.getElementById("surajSend").onclick = () => {
    const msg = input.value.trim();
    if (!msg) return;
    input.value = "";
    sendMessage(msg);
  };

  input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      document.getElementById("surajSend").click();
    }
  });

})();