// frontend/public/widget/embed.js

(function () {
  if (window.__SURAJ_WIDGET_EMBED_LOADED__) return;
  window.__SURAJ_WIDGET_EMBED_LOADED__ = true;

  /* ------------------------------------------------
     GLOBAL CONFIG
  ------------------------------------------------ */
  window.__CHAT_WIDGET_CONFIG__ = {
    name: "AI Student Assistant",
    subtitle: "Career Training School",
    color: "#0A84FF",
    logo: "logo.png",
    sound: "notify.mp3",
    apiUrl: "http://127.0.0.1:8000/chat",
    autoStart: {
      enabled: true,
      message: "👋 Hello! How can I help you today with our services?"
    }
  };

  /* ------------------------------------------------
     ✅ CLEAN + SAFE BOT MESSAGE FORMATTER
  ------------------------------------------------ */

  function formatBotMessage(text) {
    if (!text) return "";

    let formatted = text;

    /* 1️⃣ Convert URLs into clickable links (SAFE + CLEAN) */
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    formatted = formatted.replace(urlRegex, (url) => {
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="bot-link">${url}</a>`;
    });

    /* 2️⃣ Bold Pricing ($ amounts) */
    formatted = formatted.replace(
      /\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?/g,
      (match) => `<strong>${match.replace(/\s+/g, "")}</strong>`
    );

    /* 3️⃣ Bold Phone Numbers */
    formatted = formatted.replace(
      /\b\d{3}-\d{3}-\d{4}\b/g,
      "<strong>$&</strong>"
    );

    formatted = formatted.replace(
      /\(\d{3}\)\s?\d{3}-\d{4}/g,
      "<strong>$&</strong>"
    );

    /* 4️⃣ Convert dash lists (- item) into bullets */
    formatted = formatted.replace(/^\s*-\s+/gm, "• ");

    /* 5️⃣ Preserve backend line breaks */
    formatted = formatted.replace(/\n/g, "<br>");

    return formatted;
  }

  /* ------------------------------------------------
     Expose Formatter
  ------------------------------------------------ */

  window.formatBotMessage = formatBotMessage;

  window.__FORMAT_BOT_MESSAGE__ = function (message, role) {
    if (role === "bot") {
      return formatBotMessage(message);
    }
    return message;
  };

  /* ------------------------------------------------
     BANNER LAUNCHER
  ------------------------------------------------ */

  function createLauncher() {
    const launcher = document.createElement("div");
    launcher.className = "suraj-launcher";

    launcher.innerHTML = `
      <div class="suraj-label">Chat With Us</div>
      <div class="suraj-circle">
        <svg width="49" height="38" viewBox="0 0 28 28" fill="#1e3a8a">
          <path d="M21 15a4 4 0 01-4 4H8l-5 4V5a4 4 0 014-4h10a4 4 0 014 4z"/>
        </svg>
      </div>
    `;

    launcher.addEventListener("click", function () {
      if (window.toggleChatWidget) {
        window.toggleChatWidget();
      }
    });

    document.body.appendChild(launcher);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createLauncher);
  } else {
    createLauncher();
  }

  /* ------------------------------------------------
     Load widget.js
  ------------------------------------------------ */

  const script = document.createElement("script");
  script.src = "widget.js?v=" + Date.now();
  script.async = true;
  document.head.appendChild(script);

})();