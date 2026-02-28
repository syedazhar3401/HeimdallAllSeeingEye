"""
╔══════════════════════════════════════════════════════════════╗
║        HEIMDALL — YOUR VISUAL LIFE GUARDIAN                 ║
║        Majestic Nordic Fantasy Interface                    ║
║        Built with Gradio 5 + Web Speech API                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import gradio as gr
import base64
import json
import datetime
import uuid
import io
import os
import time
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from heimdall_agent import HeimdallAgent

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────
APP_TITLE = "Heimdall — Your Visual Life Guardian"
APP_VERSION = "1.0.0"

RUNES = "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛋᛏᛒᛖᛗᛚᛜᛞᛟ"

HEIMDALL_DESCRIPTION = """HEIMDALL is the Watcher at the Edge of Worlds.
He sees all that passes beneath the sky — and now, through your lens,
so shall this guardian watch over your visual reality."""

# ──────────────────────────────────────────────
# RUNE DECORATIONS
# ──────────────────────────────────────────────
RUNE_DIVIDER = "ᚠ ᛏ ᚱ ᚨ ᚲ ᛖ ᚾ ᛞ"

# ──────────────────────────────────────────────
# HTML COMPONENTS
# ──────────────────────────────────────────────

SIDEBAR_HTML = """
<div id="heimdall-sidebar">
  <!-- Logo -->
  <div id="logo-section">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="logo-icon">
      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
    </svg>
    <span class="logo-text">HEIMDALL</span>
    <span class="tagline">Always Watching</span>
    <span class="rune-divider">✦ ✧ ✦</span>
  </div>

  <!-- Session History -->
  <div id="session-section">
    <div class="section-title">PAST SESSIONS</div>
    <div id="session-history-list"></div>
    <div style="margin-top: 12px; padding: 10px; border: 1px dashed var(--border-light); border-radius: var(--radius); text-align: center;">
      <span style="font-family: 'Inter', sans-serif; font-size: 11px; color: var(--text-muted);">
        ✨ New session started ✨
      </span>
    </div>
  </div>

  <!-- Sidebar Footer -->
  <div id="sidebar-actions" style="padding: 16px; border-top: 1px solid var(--border-light);">
    <div style="font-family: 'Inter', sans-serif; font-size: 10px; color: var(--text-muted); text-align: center; letter-spacing: 1px;">
      v{version} · The Royal Guard
    </div>
  </div>
</div>
""".format(version=APP_VERSION)

TOPBAR_HTML = """
<div id="topbar">
  <div style="display:flex; align-items:center; gap:16px;">
    <button id="mobile-menu-btn"
      onclick="document.getElementById('heimdall-sidebar').classList.toggle('open')"
      style="display:none; background:transparent; border:1px solid var(--border-light);
             border-radius:var(--radius); padding:6px 10px; cursor:pointer; color:var(--text-secondary); font-size:16px;">
      ☰
    </button>
    <div class="status-indicator">
      <div class="status-dot"></div>
      <span>THE WATCHER IS ACTIVE</span>
    </div>
    <div style="font-family:'Inter', sans-serif; font-size:10px; color:var(--text-muted); letter-spacing:1px; text-transform:uppercase;">
      ✦ Realm Secure ✦
    </div>
  </div>
  <div id="topbar-right" style="display:flex; align-items:center; gap:12px;">
    <span id="session-id-display" class="session-id">SESSION: ████████</span>
    <span id="clock-display" style="font-family:'Inter', sans-serif; font-size:11px; color:var(--text-secondary); font-weight:500;"></span>
  </div>
</div>
"""

VISION_PANEL_HEADER = """
<div class="panel-header">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px; height:20px;">
    <path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z" />
    <path stroke-linecap="round" stroke-linejoin="round" d="M18.75 10.5h.008v.008h-.008V10.5Z" />
  </svg>
  THE EYES OF ASGARD
</div>
"""

CHAT_PANEL_HEADER = """
<div class="panel-header" style="color: var(--royal-gold) !important;">
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width:20px; height:20px;">
    <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
  </svg>
  THE ORACLE'S COUNSEL
</div>
"""

HEADER_HTML = """
<div style="text-align: center; margin-bottom: 24px;">
  <div style="display: flex; justify-content: center; align-items: center; gap: 16px;">
    <svg id="pulsing-eye" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" style="width: 56px; height: 56px; color: var(--pine-dark);">
      <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
    </svg>
    <h1 style="font-family: 'Cinzel Decorative', serif; font-size: 56px; color: var(--pine-dark); margin: 0; font-weight: 900; letter-spacing: 4px; line-height: 1;">HEIMDALL</h1>
  </div>
  <div style="font-family: 'Inter', sans-serif; font-size: 16px; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 12px; font-weight: 500;">
    The All-Seeing Guardian of Your World
  </div>
</div>
"""


# ──────────────────────────────────────────────
# JAVASCRIPT
# ──────────────────────────────────────────────


JS_MIC_INPUT = '''
function() {
  if (!('webkitSpeechRecognition' in window)) {
    window.showToast('Speech Recognition not supported in this browser.', '#DC2626');
    return '';
  }
  return new Promise((resolve) => {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    window.showToast('🎤 Heimdall is listening...', '#D4AF37');
    
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      window.showToast('Speech captured.', '#10B981');
      resolve(text);
    };
    recognition.onerror = (event) => {
      window.showToast('Microphone error.', '#DC2626');
      resolve('');
    };
    recognition.start();
  });
}
'''

JS_START_WATCHING = '''
function() {
  const overlay = document.getElementById('watching-overlay');
  const eye = document.getElementById('pulsing-eye');
  if (overlay) overlay.style.display = 'block';
  if (eye) eye.classList.add('pulsing');
  window.showToast('👁 THE WATCHER AWAKENS', '#D4AF37');
  
  if (!window.heimdallInterval) {
    window.heimdallInterval = setInterval(() => {
      const btn = document.querySelector('#hidden-auto-btn');
      if (btn) btn.click();
    }, 3000);
  }
  return null;
}
'''

JS_STOP_WATCHING = '''
function() {
  const overlay = document.getElementById('watching-overlay');
  const eye = document.getElementById('pulsing-eye');
  if (overlay) overlay.style.display = 'none';
  if (eye) eye.classList.remove('pulsing');
  window.showToast('⏹ THE WATCHER RESTS', '#64748B');
  
  if (window.heimdallInterval) {
    clearInterval(window.heimdallInterval);
    window.heimdallInterval = null;
  }
  return null;
}
'''

JS_SILENT_CAPTURE = '''
function() {
  const eye = document.getElementById('pulsing-eye');
  if(eye) {
    eye.style.transform = 'scale(1.2)';
    setTimeout(() => { eye.style.transform = 'scale(1)'; }, 200);
  }
  return null;
}
'''

JS_INIT = """
function() {
  // ── Theme initialization removed: Relies on native Light Mode ──

  // ── Clock ──
  function updateClock() {
    const el = document.getElementById('clock-display');
    if (el) {
      const now = new Date();
      el.textContent = now.toLocaleTimeString('en-US', {
        hour12: false, hour:'2-digit', minute:'2-digit', second:'2-digit'
      });
    }
  }
  setInterval(updateClock, 1000);
  updateClock();

  // ── Session ID from localStorage ──
  let sid = localStorage.getItem('heimdall_session_id');
  if (!sid) {
    sid = 'HMD-' + Math.random().toString(36).substr(2,8).toUpperCase();
    localStorage.setItem('heimdall_session_id', sid);
  }
  const sidEl = document.getElementById('session-id-display');
  if (sidEl) sidEl.textContent = 'SESSION: ' + sid;

  // ── Mobile menu responsive toggle ──
  const menuBtn = document.getElementById('mobile-menu-btn');
  function checkMobile() {
    if (menuBtn) menuBtn.style.display = window.innerWidth <= 768 ? 'block' : 'none';
  }
  window.addEventListener('resize', checkMobile);
  checkMobile();

  // ── Close sidebar on outside click (mobile) ──
  document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('heimdall-sidebar');
    const menuBtn = document.getElementById('mobile-menu-btn');
    if (sidebar && sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) && e.target !== menuBtn) {
      sidebar.classList.remove('open');
    }
  });

  // ── Load session history from localStorage ──
  try {
    loadSessionHistory();
  } catch(e) { console.log('History load error', e); }

  // ── Toast notification helper ──
  window.showToast = function(msg, color) {
    const toast = document.createElement('div');
    toast.className = 'notif-toast';
    toast.style.borderColor = color || '#00ff88';
    toast.style.color = color || '#00ff88';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  };

  return null;
}
"""

JS_SPEAK = """
function(text) {
  if (!text || text.trim() === '') return;
  const toggle = document.querySelector('#speaker-toggle input[type="checkbox"]');
  if (toggle && !toggle.checked) return; // Muted
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate = 0.95;
  utt.pitch = 0.85;
  utt.volume = 1.0;
  // Try to find a deep/male voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => /david|mark|george|male|en-gb/i.test(v.name));
  if (preferred) utt.voice = preferred;
  window.speechSynthesis.speak(utt);
  window.showToast('✨ HEIMDALL SPEAKS', '#D4AF37');
}
"""

JS_SNAPSHOT_FLASH = """
function() {
  const imgEls = document.querySelectorAll('.camera-frame img, .camera-frame video');
  imgEls.forEach(el => {
    el.classList.add('snapshot-flash');
    setTimeout(() => el.classList.remove('snapshot-flash'), 400);
  });
  window.showToast('📸 VISION CAPTURED', '#10B981');
  return null;
}
"""

JS_EXPORT = """
function(history_json) {
  try {
    const data = JSON.parse(history_json);
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'heimdall_session_' + new Date().toISOString().slice(0,10) + '.json';
    a.click();
    URL.revokeObjectURL(url);
    window.showToast('📜 SESSION EXPORTED TO ARCHIVES', '#10B981');
    // Save to history
    saveSessionToHistory(data);
  } catch(e) {
    window.showToast('⚠ EXPORT FAILED', '#DC2626');
  }
}
"""

JS_CLEAR = """
function() {
  window.showToast('🧹 MEMORY CLEARED', '#DC2626');
  localStorage.removeItem('heimdall_session_id');
  const newSid = 'HMD-' + Math.random().toString(36).substr(2,8).toUpperCase();
  localStorage.setItem('heimdall_session_id', newSid);
  const sidEl = document.getElementById('session-id-display');
  if (sidEl) sidEl.textContent = 'SESSION: ' + newSid;
  return null;
}
"""

JS_HISTORY = """
function saveSessionToHistory(data) {
  try {
    let hist = JSON.parse(localStorage.getItem('heimdall_history') || '[]');
    const entry = {
      id: localStorage.getItem('heimdall_session_id') || 'unknown',
      timestamp: new Date().toISOString(),
      messages: (data.messages || []).length,
      preview: (data.messages && data.messages[0]) ? data.messages[0].content : 'Empty session'
    };
    hist.unshift(entry);
    hist = hist.slice(0, 20); // keep last 20
    localStorage.setItem('heimdall_history', JSON.stringify(hist));
    loadSessionHistory();
  } catch(e) { console.log('Save history error', e); }
}

function loadSessionHistory() {
  const container = document.getElementById('session-history-list');
  if (!container) return;
  const hist = JSON.parse(localStorage.getItem('heimdall_history') || '[]');
  if (hist.length === 0) return;
  container.innerHTML = '';
  hist.forEach(function(entry) {
    const btn = document.createElement('button');
    btn.className = 'history-item-btn';
    const date = new Date(entry.timestamp);
    const dateStr = date.toLocaleDateString('en-US', {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
    btn.innerHTML = `\\`<span class="hist-title">⟨ \\${entry.id} ⟩</span>
                     <span class="hist-meta">\\${dateStr} · \\${entry.messages} msgs</span>\\``;
    btn.title = entry.preview;
    container.appendChild(btn);
  });
}
"""

FULL_HEAD_JS = f"""
<link rel="manifest" href="file/manifest.json">
<link rel="apple-touch-icon" href="file/mountains.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Orbitron:wght@400;500;600;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<script>
{JS_HISTORY}
</script>
<style>
/* Mobile sidebar */
@media (max-width: 768px) {{
  #heimdall-sidebar {{ position: fixed !important; left: -280px !important; transition: left 0.3s ease !important; height: 100vh !important; z-index: 1000 !important; }}
  #heimdall-sidebar.open {{ left: 0 !important; }}
}}
/* Custom scrollbar */
::-webkit-scrollbar {{ width: 5px; }} ::-webkit-scrollbar-track {{ background: #060d1a; }} ::-webkit-scrollbar-thumb {{ background: #00d4ff66; border-radius: 3px; }}
</style>
"""

# ──────────────────────────────────────────────
# BACK-END LOGIC
# ──────────────────────────────────────────────

def process_message(
    user_message: dict | None,
    snapshot_image,
    chat_history: list,
    use_snapshot: bool,
    agent: HeimdallAgent,
):
    audio_bytes = None
    """
    Core message handler.
    Accepts multimodal input (text + optional image from snapshot/upload)
    and appends to the chat history.
    Returns: (updated_history, last_bot_text_for_tts, export_json_str)
    """
    if chat_history is None:
        chat_history = []

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    content_parts = []
    image_for_message = None

    # ── Text from multimodal textbox ──
    text_input = ""
    if user_message and isinstance(user_message, dict):
        text_input = user_message.get("text", "") or ""
        # Attached files from the textbox itself
        files = user_message.get("files", [])
        if files:
            image_for_message = files[0]  # first attached file/image

    # ── Snapshot takes priority if enabled ──
    if use_snapshot and snapshot_image is not None:
        image_for_message = snapshot_image

    # ── Audio transcription placeholder ──
    if audio_bytes is not None and not text_input.strip():
        text_input = "[🎙 Voice message received — transcription requires a speech-to-text API]"

        return

    # ── Output Variables Setup ──
    b64_img_for_api = None

    # ── Build user message ──
    if image_for_message is not None:
        # gr.Image returns numpy array or file path
        user_msg = {"role": "user", "content": []}
        if text_input.strip():
            user_msg["content"].append({"type": "text", "text": text_input.strip()})
        # Convert image to base64 for display
        try:
            if isinstance(image_for_message, str) and os.path.exists(image_for_message):
                with open(image_for_message, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode()
                ext = Path(image_for_message).suffix.lower().replace('.', '') or 'png'
                mime = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp'] else 'image/png'
                b64_img_for_api = f"data:{mime};base64,{img_data}"
                user_msg["content"].append({
                    "type": "image_url",
                    "image_url": {"url": b64_img_for_api}
                })
            elif hasattr(image_for_message, '__array__'):
                # numpy array from webcam
                import numpy as np
                arr = image_for_message
                pil_img = Image.fromarray(arr.astype('uint8'))
                buf = io.BytesIO()
                pil_img.save(buf, format='PNG')
                img_data = base64.b64encode(buf.getvalue()).decode()
                b64_img_for_api = f"data:image/png;base64,{img_data}"
                user_msg["content"].append({
                    "type": "image_url",
                    "image_url": {"url": b64_img_for_api}
                })
        except Exception as e:
            user_msg["content"].append({"type": "text", "text": f"[Image attached — {str(e)}]"})

        if not user_msg["content"]:
            user_msg = {"role": "user", "content": text_input or "[Image]"}
    else:
        user_msg = {"role": "user", "content": text_input.strip() or "[Voice message]"}

    chat_history = chat_history + [user_msg]
    export_json = json.dumps({"session_id": "current", "messages": chat_history, "timestamp": timestamp})

    # Yield just the user message first
    yield chat_history, "", export_json

    # ── Call Heimdall ──
    response_data = agent.process(image_base64=b64_img_for_api, user_message=text_input)
    response_text = response_data.get("text", "")
    
    # Prepare Assistant Message Placeholder
    assistant_msg = {"role": "assistant", "content": ""}
    chat_history = chat_history + [assistant_msg]
    
    # ── Streaming Simulation ──
    # Yield chunk by chunk
    words = response_text.split(" ")
    accumulated_text = f"⟨ ᚹᚨᚱᛒᚱᛁᚾᚷ ⟩ — *{timestamp}* \n\n"
    
    for word in words:
        accumulated_text += word + " "
        chat_history[-1]["content"] = accumulated_text
        export_json = json.dumps({"session_id": "current", "messages": chat_history, "timestamp": timestamp})
        yield chat_history, "", export_json
        time.sleep(0.05) # Simulate slight stream delay

    # ── Plain text for TTS ──
    tts_text = response_text

    export_json = json.dumps({"session_id": "current", "messages": chat_history, "timestamp": timestamp})
    yield chat_history, tts_text, export_json


def take_snapshot(webcam_image):
    """Returns the current webcam frame as a snapshot."""
    if webcam_image is None:
        return None, gr.update(value=True)
    return webcam_image, gr.update(value=True)


def clear_memory():
    """Clears conversation history."""
    return [], "", json.dumps({"messages": []})


def export_session(chat_history):
    """Prepares session data for export."""
    export_data = {
        "session_id": "heimdall_export",
        "timestamp": datetime.datetime.now().isoformat(),
        "messages": chat_history or []
    }
    return json.dumps(export_data)


# ──────────────────────────────────────────────
# CSS LOADING
# ──────────────────────────────────────────────
def load_css() -> str:
    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


# ──────────────────────────────────────────────
# BUILD UI
# ──────────────────────────────────────────────
def build_app() -> gr.Blocks:
    custom_css = load_css()

    with gr.Blocks(
        title=APP_TITLE,
        # The theme object is saved to a variable instead, to be passed to launch()
    ) as demo:

        # ── State ──
        snapshot_state = gr.State(value=None)   # holds last snapshot
        export_json_state = gr.State(value=json.dumps({"messages": []}))
        use_snapshot_flag = gr.State(value=False)
        conversation_id = gr.State(value=lambda: str(uuid.uuid4()))
        last_image_base64 = gr.State(value=None)
        heimdall_agent_state = gr.State(value=HeimdallAgent)

        # ──────────────────────────────────────────────────────────
        # OUTER LAYOUT: 3-Column (20% - 60% - 20%)
        # ──────────────────────────────────────────────────────────
        with gr.Row(elem_id="main-wrapper"):

            # ── LEFT SIDEBAR (20%) ──
            with gr.Column(scale=1, min_width=260, elem_id="sidebar-column"):
                gr.HTML(SIDEBAR_HTML, elem_id="sidebar-html")
                
                with gr.Group(elem_classes=["sidebar-controls"]):
                    start_watch_btn = gr.Button("👁 START WATCHING", variant="primary", elem_classes=["btn-majestic", "btn-majestic-primary"])
                    stop_watch_btn = gr.Button("⏹ STOP", variant="secondary", elem_classes=["btn-majestic"])
                    snapshot_btn = gr.Button("📸 CAPTURE SNAPSHOT", variant="secondary", elem_classes=["btn-majestic"])
                    clear_btn = gr.Button("🗑 CLEAR MEMORY", variant="secondary", elem_classes=["btn-majestic", "btn-majestic-danger"])
                    use_snapshot_cb = gr.Checkbox(label="Attach to next msg", value=False, visible=False, elem_id="use-snapshot-cb")
                    hidden_auto_btn = gr.Button("hidden_auto", visible=False, elem_id="hidden-auto-btn")

            # ── CENTER WEBCAM (60%) ──
            with gr.Column(scale=3, min_width=500, elem_id="center-vision-column"):
                gr.HTML(HEADER_HTML)
                
                with gr.Group(elem_classes=["camera-frame", "massive-camera"]):
                    gr.HTML('<div id="watching-overlay" style="display:none; position:absolute; top:20px; left:20px; z-index:10; background:rgba(6,78,59,0.8); color:#D4AF37; padding:8px 16px; border-radius:8px; font-family:\'Cinzel Decorative\', serif; letter-spacing:2px; box-shadow:0 4px 12px rgba(0,0,0,0.3);">Heimdall is Watching...</div>')
                    webcam = gr.Image(
                        sources=["webcam", "upload"],
                        label="",
                        streaming=False,
                        show_label=False,
                        height=540,
                        elem_id="webcam-feed",
                        elem_classes=["majestic-webcam"],
                    )
                
                gr.HTML('<div style="font-family:\'Inter\',sans-serif; font-size:12px; font-weight:600; color:var(--text-muted); letter-spacing:2px; text-transform:uppercase; margin-top:24px; margin-bottom:12px; text-align:center;">✦ QUICK ACTIONS ✦</div>')
                with gr.Row(elem_classes=["quick-action-row"]):
                    btn_q1 = gr.Button("Organize this desk", size="sm", elem_classes=["btn-quick"])
                    btn_q2 = gr.Button("What plant is this + save it?", size="sm", elem_classes=["btn-quick"])
                    btn_q3 = gr.Button("Fix this screen error", size="sm", elem_classes=["btn-quick"])
                with gr.Row(elem_classes=["quick-action-row"]):
                    btn_q4 = gr.Button("Style this outfit", size="sm", elem_classes=["btn-quick"])
                    btn_q5 = gr.Button("Identify this object & fun facts", size="sm", elem_classes=["btn-quick"])
                    btn_q6 = gr.Button("Solve this homework", size="sm", elem_classes=["btn-quick"])

            # ── RIGHT CHAT (20%) ──
            with gr.Column(scale=1, min_width=320, elem_id="right-chat-column"):
                gr.HTML(CHAT_PANEL_HEADER)
                
                snapshot_preview = gr.Image(
                    label="", show_label=False, height=120, interactive=False, elem_id="snapshot-preview"
                )

                chatbot = gr.Chatbot(
                    value=[],
                    height=450,
                    show_label=False,
                    render_markdown=True,
                    elem_id="heimdall-chatbot",
                )
                
                with gr.Group(elem_classes=["chat-input-group"]):
                    msg_input = gr.MultimodalTextbox(
                        placeholder="Speak to Heimdall...",
                        show_label=False,
                        file_types=["image", "video"],
                        submit_btn=True,
                        elem_id="msg-input",
                    )
                    with gr.Row(elem_classes=["voice-controls"]):
                        mic_btn = gr.Button("🎤 VOICE", size="sm", elem_classes=["btn-majestic"])
                        speak_toggle = gr.Checkbox(label="Speaker Output", value=True, elem_classes=["speaker-toggle"], container=False, elem_id="speaker-toggle")
                        speak_btn = gr.Button("REPEAT", size="sm", elem_classes=["btn-majestic"])

                with gr.Row():
                    export_btn = gr.Button("EXPORT", size="sm", elem_classes=["btn-majestic"])
                    
        mic_hidden_text = gr.Textbox(visible=False, elem_id="mic-hidden-text")
        export_data_box = gr.Textbox(visible=False, elem_id="export-data")
        tts_trigger = gr.Textbox(visible=False, elem_id="tts-trigger")

        # ──────────────────────────────────────────────────────────
        # EVENT HANDLERS
        # ──────────────────────────────────────────────────────────
        
        start_watch_btn.click(fn=None, js=JS_START_WATCHING)
        stop_watch_btn.click(fn=None, js=JS_STOP_WATCHING)
        hidden_auto_btn.click(
            fn=take_snapshot,
            inputs=[webcam],
            outputs=[snapshot_preview, use_snapshot_cb],
            js=JS_SILENT_CAPTURE,
        )

        snapshot_btn.click(
            fn=take_snapshot,
            inputs=[webcam],
            outputs=[snapshot_preview, use_snapshot_cb],
            js=JS_SNAPSHOT_FLASH,
        )

        msg_input.submit(
            fn=process_message,
            inputs=[msg_input, snapshot_preview, chatbot, use_snapshot_cb, heimdall_agent_state],
            outputs=[chatbot, tts_trigger, export_data_box],
        )

        # Quick actions
        def make_submit(text):
            return {"text": text, "files": []}

        for quick_btn, default_text in [
            (btn_q1, "Organize this desk"), (btn_q2, "What plant is this + save it?"),
            (btn_q3, "Fix this screen error"), (btn_q4, "Style this outfit"),
            (btn_q5, "Identify this object & fun facts"), (btn_q6, "Solve this homework")
        ]:
            quick_btn.click(
                fn=lambda t=default_text: make_submit(t),
                inputs=[],
                outputs=[msg_input]
            ).then(
                fn=process_message,
                inputs=[msg_input, snapshot_preview, chatbot, use_snapshot_cb, heimdall_agent_state],
                outputs=[chatbot, tts_trigger, export_data_box],
            )

        mic_btn.click(
            fn=None,
            inputs=[],
            outputs=[mic_hidden_text],
            js=JS_MIC_INPUT,
        ).then(
            fn=lambda t: make_submit(t),
            inputs=[mic_hidden_text],
            outputs=[msg_input]
        )

        tts_trigger.change(
            fn=None,
            inputs=[tts_trigger],
            js=JS_SPEAK,
        )

        speak_btn.click(
            fn=None,
            inputs=[tts_trigger],
            js=JS_SPEAK,
        )

        clear_btn.click(
            fn=clear_memory,
            inputs=[],
            outputs=[chatbot, tts_trigger, export_data_box],
            js=JS_CLEAR,
        )

        export_btn.click(
            fn=export_session,
            inputs=[chatbot],
            outputs=[export_data_box],
        ).then(
            fn=None,
            inputs=[export_data_box],
            js=JS_EXPORT,
        )

        demo.load(
            fn=None,
            js=JS_INIT,
        )

    return demo, custom_css



# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("""
======================================================
       HEIMDALL — YOUR VISUAL LIFE GUARDIAN          
       Initializing Bifrost Connection...            
======================================================
    """)
    app, custom_css = build_app()
    custom_theme = gr.themes.Soft(
        primary_hue=gr.themes.Color(
            c50="#F0FDF4", c100="#DCFCE7", c200="#BBF7D0", c300="#86EFAC",
            c400="#4ADE80", c500="#22C55E", c600="#16A34A", c700="#15803D",
            c800="#166534", c900="#14532D", c950="#052E16"
        ),
        secondary_hue=gr.themes.Color(
            c50="#FEFCE8", c100="#FEF9C3", c200="#FEF08A", c300="#FDE047",
            c400="#FACC15", c500="#EAB308", c600="#CA8A04", c700="#A16207",
            c800="#854D0E", c900="#713F12", c950="#422006"
        ),
        neutral_hue=gr.themes.Color(
            c50="#F8FAFC", c100="#F1F5F9", c200="#E2E8F0", c300="#CBD5E1",
            c400="#94A3B8", c500="#64748B", c600="#475569", c700="#334155",
            c800="#1E293B", c900="#0F172A", c950="#020617"
        ),
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        font_mono=[gr.themes.GoogleFont("Fira Code"), "ui-monospace", "monospace"],
    ).set(
        body_background_fill="#F8FAFC",
        block_background_fill="#FFFFFF",
        block_border_width="1px",
        block_border_color="rgba(15, 23, 42, 0.1)",
        block_label_text_color="#64748B",
        block_shadow="0 4px 24px -4px rgba(6, 78, 59, 0.08)",
        button_primary_background_fill="#D4AF37",
        button_primary_background_fill_hover="#FBBF24",
        button_primary_text_color="#FFFFFF",
        button_secondary_background_fill="#FFFFFF",
        button_secondary_border_color="rgba(15, 23, 42, 0.1)",
        input_background_fill="#FFFFFF",
        input_border_color="rgba(15, 23, 42, 0.1)",
        input_border_color_focus="rgba(212, 175, 55, 0.4)",
    )
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        inbrowser=True,
        share=False,
        show_error=True,
        theme=custom_theme,
        css=custom_css,
        head=FULL_HEAD_JS,
    )
