#!/bin/bash
# run.sh — Запуск Джарвиса
# Работает на: Linux, macOS, Replit, VPS, Docker

set -e

# Загрузка .env если существует
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "✅ Загружен .env"
fi

# Проверка ключа
if [ -z "$GROQ_API_KEY" ]; then
  echo "❌ GROQ_API_KEY не задан."
  echo "   Создай .env из .env.example или задай переменную:"
  echo "   export GROQ_API_KEY=gsk_..."
  exit 1
fi

# Установка зависимостей если нужно
if ! python -c "import streamlit, groq" 2>/dev/null; then
  echo "📦 Установка зависимостей..."
  pip install -r requirements.txt -q
fi

echo "🚀 Запуск Джарвиса..."
streamlit run app.py \
  --server.port="${PORT:-8501}" \
  --server.address="0.0.0.0" \
  --server.headless=true \
  --browser.gatherUsageStats=false \
  "$@"
