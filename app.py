"""
app.py — Джарвис v2.0
Платформонезависимый: Replit, ПК, VPS, Docker.
Все настройки — в config.py. Дизайн — в styles.py.

Исправления v2:
  • Удалены мёртвые импорты из database.py (система авторизации не использовалась)
  • build_zip() работает правильно — ищет файлы относительно директории скрипта
  • Карточки-подсказки теперь кликабельны (inject через session_state)
  • CSS применяется сразу при первом рендере
  • Улучшен fallback для text-модели
  • Исправлен UX: чипы + карточки + ввод — единая система
  • Новый дизайн: Neural Obsidian
"""
import os
import base64
import io
import zipfile
from pathlib import Path

import streamlit as st
from groq import Groq

import config
from styles import get_css, PWA_JS, CHAT_JS

# ─────────────────────────────────────────────────────────────
#  Конфигурация страницы (первый вызов Streamlit)
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.markdown(PWA_JS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  Groq клиент (один на весь сервер)
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_groq() -> Groq:
    if not config.GROQ_API_KEY:
        st.error(
            "❌ **GROQ_API_KEY не задан.**\n\n"
            "• Replit: Secrets → GROQ_API_KEY\n"
            "• ПК: `export GROQ_API_KEY=gsk_...`\n"
            "• Получить бесплатно: https://console.groq.com"
        )
        st.stop()
    return Groq(api_key=config.GROQ_API_KEY)


def ask_jarvis(messages: list, img_b64: str = None, img_mime: str = None) -> str:
    """Отправляет запрос в Groq и возвращает ответ."""
    client  = get_groq()
    context = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    context += messages[-config.MAX_CONTEXT:]

    # Запрос с изображением (vision)
    if img_b64:
        last = context[-1]
        context[-1] = {
            "role": "user",
            "content": [
                {"type": "text",      "text": last.get("content", "Опиши что на этом изображении.")},
                {"type": "image_url", "image_url": {"url": f"data:{img_mime};base64,{img_b64}"}},
            ],
        }
        for model in [config.VISION_MODEL, config.VISION_FALLBACK]:
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=context,
                    max_tokens=config.MAX_TOKENS,
                    temperature=config.TEMPERATURE,
                )
                return resp.choices[0].message.content
            except Exception:
                continue
        return "⚠️ Vision-модели временно недоступны. Опишите изображение текстом, сэр."

    # Текстовый запрос — с fallback на быструю модель
    for model in [config.TEXT_MODEL, config.TEXT_FAST]:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=context,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
            )
            return resp.choices[0].message.content
        except Exception:
            continue

    return "⚠️ Groq API временно недоступен. Повторите запрос через несколько секунд, сэр."

# ─────────────────────────────────────────────────────────────
#  Сессия
# ─────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "ok":          True,
        "messages":    [],
        "pending_img": None,
        "theme":       "dark",
        "_inject":     None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ─────────────────────────────────────────────────────────────
#  Изображения
# ─────────────────────────────────────────────────────────────

MIME_MAP = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "png": "image/png",  "webp": "image/webp", "gif": "image/gif",
}

def store_image(file) -> None:
    data = file.read()
    ext  = file.name.rsplit(".", 1)[-1].lower()
    mime = MIME_MAP.get(ext, "image/jpeg")
    st.session_state["pending_img"] = {
        "b64":  base64.b64encode(data).decode(),
        "mime": mime,
        "name": file.name,
    }

# ─────────────────────────────────────────────────────────────
#  ZIP для скачивания
# ─────────────────────────────────────────────────────────────

def build_zip() -> bytes:
    """Собирает ZIP с исходниками проекта."""
    root = Path(__file__).parent          # директория, где лежит app.py
    files = [
        "app.py", "config.py", "database.py", "styles.py",
        "requirements.txt", ".env.example", "run.sh",
    ]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in files:
            fpath = root / fname
            if fpath.exists():
                zf.write(fpath, fname)
    return buf.getvalue()

# ─────────────────────────────────────────────────────────────
#  Сайдбар
# ─────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"<h2 style='font-family:var(--mono,monospace);font-size:1rem;"
            f"letter-spacing:0.1em;margin:0 0 4px'>"
            f"<span style='color:var(--accent,#4F8EF7)'>⚡</span> JARVIS v{config.VERSION}</h2>",
            unsafe_allow_html=True,
        )
        st.caption("Персональный ИИ-ассистент")
        st.divider()

        # Тема
        theme_val = st.radio(
            "Тема",
            ["🌙 Тёмная", "☀️ Светлая"],
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
            horizontal=True,
            key="theme_radio",
        )
        new_theme = "dark" if "Тёмная" in theme_val else "light"
        if st.session_state.get("theme") != new_theme:
            st.session_state["theme"] = new_theme
            st.rerun()

        st.divider()

        # Очистить чат
        if st.button("🗑 Очистить историю", use_container_width=True):
            st.session_state["messages"]    = []
            st.session_state["pending_img"] = None
            st.rerun()

        st.divider()

        # Скачать проект
        st.caption("**Скачать проект**")
        st.download_button(
            label="📦 jarvis_project.zip",
            data=build_zip(),
            file_name="jarvis_project.zip",
            mime="application/zip",
            use_container_width=True,
        )

        st.divider()

        # Настройки
        with st.expander("⚙ Конфигурация"):
            st.code(
                f"Модель:   {config.TEXT_MODEL}\n"
                f"Vision:   {config.VISION_MODEL}\n"
                f"Контекст: {config.MAX_CONTEXT} сообщ.\n"
                f"Токены:   {config.MAX_TOKENS}\n"
                f"БД:       {'PostgreSQL' if config.DATABASE_URL else 'SQLite'}",
                language=None,
            )
            st.caption("Изменяется в `config.py`")

        # Статистика сессии
        msg_count = len(st.session_state.get("messages", []))
        if msg_count:
            with st.expander(f"📊 Сессия ({msg_count // 2} обменов)"):
                user_msgs = sum(1 for m in st.session_state["messages"] if m["role"] == "user")
                st.markdown(f"• Запросов: **{user_msgs}**")
                st.markdown(f"• Ответов: **{msg_count - user_msgs}**")

        st.divider()
        st.caption(f"Jarvis AI · Groq × Llama\n© Sardarbek Kurbanaliev")

# ─────────────────────────────────────────────────────────────
#  Главный экран чата
# ─────────────────────────────────────────────────────────────

def send_message(text: str):
    """Инжектирует сообщение как будто пользователь его написал."""
    st.session_state["_inject"] = text
    st.rerun()


def show_chat():
    theme = st.session_state.get("theme", "dark")
    msgs  = st.session_state.get("messages", [])

    render_sidebar()

    # Всегда рендерим CSS с правильной темой
    st.markdown(get_css(theme), unsafe_allow_html=True)
    st.markdown(CHAT_JS, unsafe_allow_html=True)

    # ── Загрузка изображения ────────────────────────────────
    uploaded = st.file_uploader(
        "Прикрепить изображение",
        type=list(MIME_MAP.keys()),
        key="fu",
        label_visibility="collapsed",
    )
    if uploaded:
        pimg = st.session_state.get("pending_img") or {}
        if pimg.get("name") != uploaded.name:
            store_image(uploaded)

    pimg = st.session_state.get("pending_img")
    if pimg:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.image(f"data:{pimg['mime']};base64,{pimg['b64']}", width=180)
        with col2:
            if st.button("✕", key="rmimg", help="Убрать фото"):
                st.session_state["pending_img"] = None
                st.rerun()

    # ── Пустой экран — hero + карточки ─────────────────────
    if not msgs:
        st.markdown(
            '<div class="jv-hero">'
            '<div class="jv-badge">NEURAL AI · GROQ × LLAMA</div>'
            '<div class="jv-logo">JAR<span>V</span>IS</div>'
            '<p class="jv-sub">Персональный ИИ-ассистент нового поколения.<br>'
            'Задайте вопрос или выберите подсказку ниже.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Карточки — кликабельные через кнопки Streamlit
        cols = st.columns(2)
        for i, (title, sub) in enumerate(config.SUGGEST_CARDS):
            with cols[i % 2]:
                if st.button(
                    f"**{title}**\n{sub}",
                    key=f"card_{i}",
                    use_container_width=True,
                ):
                    send_message(f"{title}: {sub}")

    else:
        # ── История сообщений ──────────────────────────────
        for msg in msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ── Быстрые чипы ────────────────────────────────────────
    cols = st.columns(len(config.CHIPS))
    for i, (label, cmd) in enumerate(config.CHIPS):
        with cols[i]:
            if st.button(label, key=f"chip_{i}", use_container_width=True):
                if cmd == "__clear__":
                    st.session_state["messages"]    = []
                    st.session_state["pending_img"] = None
                    st.rerun()
                else:
                    send_message(cmd)

    # ── Поле ввода ───────────────────────────────────────────
    injected = st.session_state.pop("_inject", None)
    prompt   = injected or st.chat_input(config.PLACEHOLDER)

    if prompt:
        pi    = st.session_state.get("pending_img")
        ib64  = pi["b64"]  if pi else None
        imime = pi["mime"] if pi else None

        # Показываем сообщение пользователя
        with st.chat_message("user"):
            if pi:
                st.image(f"data:{pi['mime']};base64,{pi['b64']}", width=180)
            st.markdown(prompt)

        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.session_state["pending_img"] = None

        # Показываем ответ ассистента
        with st.chat_message("assistant"):
            slot = st.empty()
            slot.markdown(
                '<div class="jv-typing">'
                '<span></span><span></span><span></span>'
                '</div>',
                unsafe_allow_html=True,
            )
            try:
                reply = ask_jarvis(st.session_state["messages"], ib64, imime)
            except Exception as e:
                reply = f"⚠️ Ошибка API: `{e}`\n\nПроверьте GROQ_API_KEY и подключение к интернету."
            slot.markdown(reply)

        st.session_state["messages"].append({"role": "assistant", "content": reply})
        st.rerun()

# ─────────────────────────────────────────────────────────────
#  Точка входа
# ─────────────────────────────────────────────────────────────

def main():
    init_session()
    show_chat()


if __name__ == "__main__":
    main()
