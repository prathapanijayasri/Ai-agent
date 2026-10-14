document.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chatMessages");
  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const exampleQuestions = document.getElementById("exampleQuestions");
  const charCounter = document.getElementById("charCounter");

  // Health and System Status
  const systemStatusText = document.getElementById("systemStatusText");

  // Modal elements
  const uploadModalBtn = document.getElementById("uploadModalBtn");
  const uploadModal = document.getElementById("uploadModal");
  const closeModalBtn = document.getElementById("closeModalBtn");
  const cancelUploadBtn = document.getElementById("cancelUploadBtn");
  const uploadForm = document.getElementById("uploadForm");
  const fileInput = document.getElementById("fileInput");
  const selectedFileName = document.getElementById("selectedFileName");
  const adminKeyInput = document.getElementById("adminKeyInput");
  const uploadFeedback = document.getElementById("uploadFeedback");
  const startUploadBtn = document.getElementById("startUploadBtn");

  // Check backend health
  checkHealth();

  // Character counter and Auto-resize textarea
  messageInput.addEventListener("input", () => {
    charCounter.textContent = `${messageInput.value.length} / 2000`;
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
  });

  // Enter to send (Shift + Enter for new line)
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (messageInput.value.trim().length > 0 && !sendBtn.disabled) {
        chatForm.dispatchEvent(new Event("submit"));
      }
    }
  });

  // Quick prompt chips
  exampleQuestions.addEventListener("click", (e) => {
    const chip = e.target.closest(".example-chip");
    if (chip) {
      const prompt = chip.dataset.prompt;
      messageInput.value = prompt;
      charCounter.textContent = `${prompt.length} / 2000`;
      messageInput.focus();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Chat Submission
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = messageInput.value.trim();
    if (!query) return;

    // Append User Message
    appendMessage("user", query);
    messageInput.value = "";
    messageInput.style.height = "auto";
    charCounter.textContent = "0 / 2000";

    // Disable input and show loading indicator
    setLoading(true);

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: query })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to retrieve response from MediBot.");
      }

      appendMessage("bot", data.response, {
        isEmergency: data.is_emergency,
        sources: data.sources || [],
        provider: data.provider,
        reliableContext: data.reliable_context
      });

    } catch (err) {
      appendMessage("bot", `⚠️ **Notice:** ${err.message || "Unable to reach the MediBot service. Please verify your connection."}`, {
        isError: true
      });
    } finally {
      setLoading(false);
      messageInput.focus();
    }
  });

  // Append Message Helper
  function appendMessage(sender, text, options = {}) {
    const isBot = sender === "bot";
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${isBot ? "bot-message" : "user-message"}`;

    if (options.isEmergency) {
      msgDiv.classList.add("emergency-alert");
    }

    const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let avatarSvg = isBot
      ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M2 12h20"/></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`;

    if (options.isEmergency) {
      avatarSvg = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    }

    let sourcesHtml = "";
    if (options.sources && options.sources.length > 0) {
      const sourceList = options.sources.map(s => {
        return `<div class="source-item">
          <span class="source-pill">${escapeHtml(s.source)} (p. ${s.page || 1})</span>
          <span>${escapeHtml(s.snippet)}</span>
        </div>`;
      }).join("");

      sourcesHtml = `
        <div class="sources-container">
          <div class="sources-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
            <span>Verified Knowledge Citations</span>
          </div>
          <div class="sources-list">${sourceList}</div>
        </div>
      `;
    }

    const providerTag = options.provider
      ? `<div class="provider-tag">Response generated via: ${escapeHtml(options.provider)}</div>`
      : "";

    msgDiv.innerHTML = `
      <div class="message-avatar">${avatarSvg}</div>
      <div class="message-body">
        <div class="message-header">
          <span class="sender-name">${isBot ? "MediBot AI" : "You"}</span>
          <span class="message-time">${timeString}</span>
        </div>
        <div class="message-content">${formatMarkdown(text)}</div>
        ${sourcesHtml}
        ${providerTag}
      </div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function setLoading(isLoading) {
    if (isLoading) {
      loadingIndicator.style.display = "flex";
      sendBtn.disabled = true;
    } else {
      loadingIndicator.style.display = "none";
      sendBtn.disabled = false;
    }
  }

  // Health check
  async function checkHealth() {
    try {
      const res = await fetch("/health");
      if (res.ok) {
        const data = await res.json();
        systemStatusText.textContent = `Online (${data.indexed_chunks || 0} chunks)`;
      } else {
        systemStatusText.textContent = "Degraded";
      }
    } catch {
      systemStatusText.textContent = "Offline";
    }
  }

  // Modal Handlers
  uploadModalBtn.addEventListener("click", () => {
    uploadModal.classList.add("active");
    uploadFeedback.style.display = "none";
    fileInput.value = "";
    selectedFileName.textContent = "";
  });

  const closeModal = () => {
    uploadModal.classList.remove("active");
  };

  closeModalBtn.addEventListener("click", closeModal);
  cancelUploadBtn.addEventListener("click", closeModal);

  uploadModal.addEventListener("click", (e) => {
    if (e.target === uploadModal) closeModal();
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      selectedFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    } else {
      selectedFileName.textContent = "";
    }
  });

  // Handle document upload
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!fileInput.files.length) return;

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const adminKey = adminKeyInput.value.trim();
    const headers = {};
    if (adminKey) {
      headers["X-Admin-Key"] = adminKey;
    }

    startUploadBtn.disabled = true;
    startUploadBtn.textContent = "Ingesting...";
    uploadFeedback.style.display = "none";

    try {
      const res = await fetch("/documents", {
        method: "POST",
        headers: headers,
        body: formData
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to ingest document");
      }

      uploadFeedback.className = "upload-feedback success";
      uploadFeedback.textContent = `Success! Ingested ${data.chunks_ingested} chunk(s) from "${data.filename}". Total index count: ${data.total_indexed_chunks}.`;
      uploadFeedback.style.display = "block";

      checkHealth();

      setTimeout(() => {
        closeModal();
      }, 2000);

    } catch (err) {
      uploadFeedback.className = "upload-feedback error";
      uploadFeedback.textContent = `Error: ${err.message}`;
      uploadFeedback.style.display = "block";
    } finally {
      startUploadBtn.disabled = false;
      startUploadBtn.innerHTML = `<span>Upload & Ingest</span>`;
    }
  });

  // Lightweight Markdown Formatter
  function formatMarkdown(text) {
    if (!text) return "";
    let safe = escapeHtml(text);

    // Bold
    safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italics
    safe = safe.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Headers
    safe = safe.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    safe = safe.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    safe = safe.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    // Unordered lists
    safe = safe.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
    safe = safe.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
    // Paragraph breaks
    safe = safe.replace(/\n\n+/g, '</p><p>');
    safe = safe.replace(/\n/g, '<br>');

    return `<p>${safe}</p>`;
  }

  function escapeHtml(string) {
    const entityMap = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    };
    return String(string).replace(/[&<>"']/g, s => entityMap[s]);
  }
});
