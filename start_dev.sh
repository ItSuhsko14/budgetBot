#!/bin/bash

echo "🚀 Запуск ngrok..."
ngrok http 8443 > /dev/null &

# Очікуємо поки ngrok запуститься
sleep 2

# Отримуємо публічну адресу ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ -z "$NGROK_URL" ]; then
  echo "❌ Не вдалося отримати адресу ngrok"
  exit 1
fi

WEBHOOK_URL="${NGROK_URL}"
echo "🌐 WEBHOOK_URL: $WEBHOOK_URL"

# 🔁 Оновлюємо .env
ENV_FILE=".env"

# Якщо файл існує — замінюємо WEBHOOK_URL
if [ -f "$ENV_FILE" ]; then
  sed -i "" -E "s|^WEBHOOK_URL=.*|WEBHOOK_URL=$WEBHOOK_URL|" "$ENV_FILE"
  echo "✅ Оновлено WEBHOOK_URL у $ENV_FILE"
else
  echo "❌ Файл $ENV_FILE не знайдено!"
  exit 1
fi

echo "✅ Змінні з .env завантажено"
export $(grep -v '^#' .env | xargs)

echo "📦 Запуск застосунку з main.py"
python3 main.py