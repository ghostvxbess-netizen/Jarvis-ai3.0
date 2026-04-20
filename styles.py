"""
styles.py — Эксклюзивный дизайн Джарвиса v2.
Концепция: «Neural Obsidian» — тёмный, острый, технологичный.
Акцент — электрический синий (#4F8EF7) вместо зелёного ChatGPT.
Типографика: IBM Plex Mono + IBM Plex Sans.
"""

# ── PWA / Viewport ────────────────────────────────────────────
PWA_JS = """
<script>
(function() {
  function setViewport() {
    var v = document.querySelector('meta[name="viewport"]');
    var c = 'width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover';
    if (v) { v.content = c; } else {
      var m = document.createElement('meta');
      m.name = 'viewport'; m.content = c;
      document.head.appendChild(m);
    }
  }
  setViewport();
  setTimeout(setViewport, 200);
  setTimeout(setViewport, 800);

  // Google Fonts
  if (!document.getElementById('jv-fonts')) {
    var l = document.createElement('link');
    l.id = 'jv-fonts';
    l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap';
    document.head.appendChild(l);
  }

  // PWA мета-теги
  [
    ['apple-mobile-web-app-capable',        'yes'],
    ['apple-mobile-web-app-status-bar-style','black-translucent'],
    ['apple-mobile-web-app-title',          'Jarvis'],
    ['theme-color',                         '#080b12'],
    ['mobile-web-app-capable',              'yes'],
  ].forEach(function(p) {
    if (!document.querySelector('meta[name="' + p[0] + '"]')) {
      var m = document.createElement('meta');
      m.name = p[0]; m.content = p[1];
      document.head.appendChild(m);
    }
  });
})();
</script>"""

# ── Темы ──────────────────────────────────────────────────────
DARK = {
    "bg":       "#080b12",
    "bg2":      "#0d1117",
    "bg3":      "#131920",
    "bg4":      "#1a2233",
    "input":    "#0f1724",
    "text":     "#e8edf5",
    "sub":      "#6b7a96",
    "dim":      "#2a3347",
    "border":   "rgba(79,142,247,0.12)",
    "accent":   "#4F8EF7",
    "accent2":  "#7BAEFF",
    "glow":     "rgba(79,142,247,0.18)",
    "user_bg":  "#111827",
    "code_bg":  "#0a0f1a",
    "font_ui":  "'IBM Plex Sans', system-ui, sans-serif",
    "font_mono":"'IBM Plex Mono', 'Fira Code', monospace",
}

LIGHT = {
    "bg":       "#f4f6fb",
    "bg2":      "#eaecf4",
    "bg3":      "#dde1ef",
    "bg4":      "#d0d6e8",
    "input":    "#ffffff",
    "text":     "#0d1117",
    "sub":      "#5a6480",
    "dim":      "#c5cbdc",
    "border":   "rgba(79,142,247,0.18)",
    "accent":   "#2d6ff0",
    "accent2":  "#4F8EF7",
    "glow":     "rgba(79,142,247,0.12)",
    "user_bg":  "#e8ecf8",
    "code_bg":  "#f0f2fa",
    "font_ui":  "'IBM Plex Sans', system-ui, sans-serif",
    "font_mono":"'IBM Plex Mono', 'Fira Code', monospace",
}

# ── Базовый CSS ────────────────────────────────────────────────
BASE_CSS = """
/* ── Скрываем стандартный UI Streamlit ── */
#MainMenu, footer, header,
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display: none !important; }}

/* ── CSS-переменные темы ── */
:root {{
  --bg:        {bg};
  --bg2:       {bg2};
  --bg3:       {bg3};
  --bg4:       {bg4};
  --input:     {input};
  --text:      {text};
  --sub:       {sub};
  --dim:       {dim};
  --border:    {border};
  --accent:    {accent};
  --accent2:   {accent2};
  --glow:      {glow};
  --user-bg:   {user_bg};
  --code-bg:   {code_bg};
  --font:      {font_ui};
  --mono:      {font_mono};
  --r:         12px;
  --r-lg:      20px;
  --safe-b:    env(safe-area-inset-bottom, 0px);
}}

/* ── Сброс и базовые стили ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  background: var(--bg) !important;
  font-family: var(--font) !important;
  color: var(--text) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}}

/* ── App контейнер ── */
.stApp {{
  background: var(--bg) !important;
  transition: height 0.1s ease;
}}

/* Тонкая сетка на фоне (декор) */
.stApp::before {{
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
  opacity: 0.4;
}}

.main {{ background: transparent !important; position: relative; z-index: 1; }}

.block-container {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  max-width: 760px !important;
  width: 100% !important;
  margin: 0 auto !important;
  padding: 1.5rem 1.2rem 220px 1.2rem !important;
  position: relative;
  z-index: 1;
}}

/* ── Сайдбар ── */
[data-testid="stSidebar"] {{
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
[data-testid="stSidebar"] .stMarkdown h2 {{
  font-family: var(--mono) !important;
  font-size: 1rem !important;
  letter-spacing: 0.08em !important;
  color: var(--accent) !important;
}}

/* ── Типографика ── */
h1, h2, h3 {{
  font-family: var(--font) !important;
  color: var(--text) !important;
  font-weight: 600 !important;
}}
p, li {{ color: var(--text) !important; }}
span {{ color: inherit !important; }}
label {{ color: var(--sub) !important; font-size: 0.82rem !important; }}

/* ── Поле ввода (обычное) ── */
.stTextInput > div > div > input {{
  background: var(--input) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.95rem !important;
  padding: 0.7rem 1rem !important;
  -webkit-appearance: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}}
.stTextInput > div > div > input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--glow) !important;
  outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{ color: var(--sub) !important; }}

/* ── Кнопки — основные (chip) ── */
.stButton > button {{
  background: var(--bg3) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  font-family: var(--font) !important;
  font-size: 0.87rem !important;
  font-weight: 500 !important;
  min-height: 44px !important;
  padding: 0.55rem 0.8rem !important;
  width: 100% !important;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-appearance: none;
  touch-action: manipulation;
  letter-spacing: 0.01em;
}}
.stButton > button:hover {{
  background: var(--bg4) !important;
  border-color: var(--accent) !important;
  color: var(--accent2) !important;
  box-shadow: 0 0 12px var(--glow) !important;
}}
.stButton > button:active {{
  transform: scale(0.97) !important;
  opacity: 0.85 !important;
}}

/* ── Кнопки скачивания ── */
[data-testid="stDownloadButton"] > button {{
  background: transparent !important;
  color: var(--sub) !important;
  border: 1px solid var(--dim) !important;
  border-radius: var(--r) !important;
  font-family: var(--mono) !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  min-height: 40px !important;
  letter-spacing: 0.04em;
  padding: 0.5rem 1rem !important;
  width: 100% !important;
  transition: all 0.18s;
}}
[data-testid="stDownloadButton"] > button:hover {{
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}}

/* ── Сообщения чата ── */
[data-testid="stChatMessage"] {{
  background: transparent !important;
  border: none !important;
  padding: 0.5rem 0 !important;
}}
[data-testid="stChatMessage"] p {{
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.96rem !important;
  line-height: 1.78 !important;
}}

/* Пузырь пользователя */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
  background: var(--user-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-lg) !important;
  padding: 0.9rem 1.1rem !important;
  margin-bottom: 0.2rem;
}}

/* Код в сообщениях */
[data-testid="stChatMessage"] code {{
  background: var(--code-bg) !important;
  color: var(--accent2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  padding: 0.12em 0.45em !important;
  font-family: var(--mono) !important;
  font-size: 0.87em !important;
}}
[data-testid="stChatMessage"] pre {{
  background: var(--code-bg) !important;
  border: 1px solid var(--border) !important;
  border-left: 3px solid var(--accent) !important;
  border-radius: var(--r) !important;
  padding: 1.1rem 1rem !important;
  overflow-x: auto;
  font-family: var(--mono) !important;
  font-size: 0.88rem !important;
}}
[data-testid="stChatMessage"] pre code {{
  background: transparent !important;
  border: none !important;
  color: var(--text) !important;
  padding: 0 !important;
}}

/* ── Поле ввода чата ── */
[data-testid="stBottom"] {{
  background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
  border-top: none !important;
  padding-bottom: calc(var(--safe-b) + 6px) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}}
[data-testid="stChatInput"] {{
  background: var(--input) !important;
  border: 1px solid var(--border) !important;
  border-radius: 24px !important;
  transition: border-color 0.2s, box-shadow 0.2s;
}}
[data-testid="stChatInput"]:focus-within {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--glow), 0 4px 24px rgba(0,0,0,0.3) !important;
}}
[data-testid="stChatInput"] textarea {{
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.97rem !important;
  background: transparent !important;
  caret-color: var(--accent) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: var(--sub) !important; }}

/* ── Загрузчик файлов ── */
[data-testid="stFileUploader"] {{
  background: var(--bg2) !important;
  border: 1px dashed var(--dim) !important;
  border-radius: var(--r) !important;
  transition: border-color 0.2s;
}}
[data-testid="stFileUploader"]:hover {{
  border-color: var(--accent) !important;
}}
[data-testid="stFileUploader"] p {{ color: var(--sub) !important; font-size: 0.85rem !important; }}
[data-testid="stFileUploader"] small {{ color: var(--dim) !important; }}

/* ── Алерты ── */
.stAlert {{
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
}}

/* ── Радио-кнопки (тема) ── */
.stRadio > div {{
  gap: 8px !important;
}}
.stRadio label {{ color: var(--sub) !important; }}
.stRadio [data-testid="stMarkdownContainer"] p {{
  color: var(--text) !important;
  font-size: 0.9rem !important;
}}

/* ── Разделитель ── */
hr {{ border-color: var(--dim) !important; opacity: 0.5; }}

/* ── Hero (пустой экран) ── */
.jv-hero {{
  text-align: center;
  padding: 3rem 0 1.5rem;
  animation: fadeInUp 0.5s ease both;
}}
.jv-badge {{
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--accent);
  border: 1px solid var(--border);
  background: var(--glow);
  border-radius: 999px;
  padding: 0.3em 1em;
  margin-bottom: 1.2rem;
}}
.jv-logo {{
  font-family: var(--mono);
  font-size: 2.6rem;
  font-weight: 400;
  color: var(--text);
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 0.5rem;
}}
.jv-logo span {{ color: var(--accent); }}
.jv-sub {{
  font-size: 0.9rem;
  color: var(--sub);
  line-height: 1.5;
}}

/* ── Карточки подсказок ── */
.jv-cards {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 1.5rem 0 1rem;
}}
.jv-card {{
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  animation: fadeInUp 0.5s ease both;
}}
.jv-card:hover {{
  background: var(--bg3);
  border-color: var(--accent);
  box-shadow: 0 0 16px var(--glow);
  transform: translateY(-1px);
}}
.jv-card b {{
  display: block;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
  font-family: var(--font);
}}
.jv-card span {{
  font-size: 0.77rem;
  color: var(--sub);
  line-height: 1.4;
  font-family: var(--font);
}}

/* ── Индикатор набора ── */
.jv-typing {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0.4rem 0;
}}
.jv-typing span {{
  width: 7px; height: 7px;
  background: var(--accent);
  border-radius: 50%;
  display: inline-block;
  animation: jv-bounce 1.2s infinite ease-in-out;
  opacity: 0.6;
}}
.jv-typing span:nth-child(2) {{ animation-delay: 0.2s; }}
.jv-typing span:nth-child(3) {{ animation-delay: 0.4s; }}

@keyframes jv-bounce {{
  0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
  30%            {{ transform: translateY(-6px); opacity: 1; }}
}}

/* ── Иконка ассистента ── */
[data-testid="chatAvatarIcon-assistant"] {{
  background: linear-gradient(135deg, var(--accent), #7B3FE4) !important;
  border-radius: 8px !important;
}}

/* ── Полоса прокрутки ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
  background: var(--dim);
  border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{ background: var(--sub); }}

/* ── Анимации ── */
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ── Мобильный ── */
@media (max-width: 768px) {{
  .block-container {{
    padding: 0.8rem 0.6rem 190px !important;
    max-width: 100% !important;
  }}
  .jv-hero {{ padding: 1.8rem 0 1rem; }}
  .jv-logo {{ font-size: 1.9rem; }}
  .jv-cards {{ gap: 8px; }}
  .stButton > button {{ font-size: 0.82rem !important; min-height: 42px !important; }}
  [data-testid="stChatInput"] textarea {{ font-size: 16px !important; }}
}}
"""

# ── JavaScript для чата ───────────────────────────────────────
CHAT_JS = """
<script>
(function() {
  function initChat() {
    function scrollEl() {
      return document.querySelector('[data-testid="stAppViewBlockContainer"]')
          || document.querySelector('.main')
          || document.documentElement;
    }

    function scrollToBottom() {
      var el = scrollEl();
      if (el) el.scrollTop = el.scrollHeight;
      window.scrollTo(0, document.body.scrollHeight);
    }

    // MutationObserver — скролл при новых сообщениях
    var observer = new MutationObserver(function() { scrollToBottom(); });
    function startObserving() {
      var el = scrollEl();
      if (el) observer.observe(el, { childList: true, subtree: true });
    }

    // Фиксация виртуальной клавиатуры (iOS/Android)
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', function() {
        var h = window.innerHeight - window.visualViewport.height;
        var bottom = document.querySelector('[data-testid="stBottom"]');
        if (bottom) bottom.style.paddingBottom = (h + 6) + 'px';
        scrollToBottom();
      });
    }

    scrollToBottom();
    setTimeout(function() { startObserving(); scrollToBottom(); }, 400);
    setTimeout(scrollToBottom, 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChat);
  } else {
    initChat();
  }
})();
</script>
"""


def get_css(theme: str = "dark") -> str:
    t = DARK if theme == "dark" else LIGHT
    return f"<style>{BASE_CSS.format(**t)}</style>"
