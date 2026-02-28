import re

with open(r'c:\Users\Syed\Documents\Mistral Hackathon\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new Javascript blocks
NEW_JS = """
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
"""

# Replace the JS_SPEAK to respect speaker toggle
OLD_JS_SPEAK = """JS_SPEAK = \"\"\"
function(text) {
  if (!text || text.trim() === '') return;
  if (!window.speechSynthesis) return;"""

NEW_JS_SPEAK = """JS_SPEAK = \"\"\"
function(text) {
  if (!text || text.trim() === '') return;
  const toggle = document.querySelector('#speaker-toggle input[type="checkbox"]');
  if (toggle && !toggle.checked) return; // Muted
  if (!window.speechSynthesis) return;"""


# Layout Replacement
OLD_LAYOUT_START = """        # ──────────────────────────────────────────────────────────
        # OUTER LAYOUT: Sidebar + Main
        # ──────────────────────────────────────────────────────────"""
NEW_LAYOUT = """        # ──────────────────────────────────────────────────────────
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
                    gr.HTML('<div id="watching-overlay" style="display:none; position:absolute; top:20px; left:20px; z-index:10; background:rgba(6,78,59,0.8); color:#D4AF37; padding:8px 16px; border-radius:8px; font-family:\\'Cinzel Decorative\\', serif; letter-spacing:2px; box-shadow:0 4px 12px rgba(0,0,0,0.3);">Heimdall is Watching...</div>')
                    webcam = gr.Image(
                        sources=["webcam", "upload"],
                        label="",
                        streaming=False,
                        show_label=False,
                        height=540,
                        elem_id="webcam-feed",
                        elem_classes=["majestic-webcam"],
                    )
                
                gr.HTML('<div style="font-family:\\'Inter\\',sans-serif; font-size:12px; font-weight:600; color:var(--text-muted); letter-spacing:2px; text-transform:uppercase; margin-top:24px; margin-bottom:12px; text-align:center;">✦ QUICK ACTIONS ✦</div>')
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
            inputs=[msg_input, None, snapshot_preview, chatbot, use_snapshot_cb],
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
                inputs=[msg_input, None, snapshot_preview, chatbot, use_snapshot_cb],
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
"""


# Combine into a final replacement strategy
# First inject NEW_JS before JS_INIT
content = content.replace("JS_INIT = \"\"\"", NEW_JS + "\\n\\nJS_INIT = \"\"\"")

# Then modify JS_SPEAK
content = content.replace(OLD_JS_SPEAK, NEW_JS_SPEAK)

# Then replace layout and handlers.
# Find where layout starts and where the return statement is.
start_idx = content.find(OLD_LAYOUT_START)
end_idx = content.find("    return demo, custom_css") + len("    return demo, custom_css")

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + NEW_LAYOUT + content[end_idx:]
    with open(r'c:\Users\Syed\Documents\Mistral Hackathon\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully replaced layout in app.py")
else:
    print("Failed to find layout boundaries.", start_idx, end_idx)
