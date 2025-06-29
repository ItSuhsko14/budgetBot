import requests
from telegram import Bot
from utils.logger import log  # якщо у тебе є логер
from utils.env_loader import load_env
import os
from utils.logger import log
from deep_translator import GoogleTranslator

# 🔑 Hugging Face Token
load_env()
API_KEY_HF = os.environ.get("API_KEY_HF")
HF_API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
HEADERS = {"Authorization": f"Bearer {API_KEY_HF}"}

# Додаємо перевірку API ключа
# Перевіряємо наявність API ключа
if not API_KEY_HF:
    log("❌ Помилка: API_KEY_HF не знайдено в змінних оточення")
    log("Будь ласка, додайте API_KEY_HF у файл .env")
    HEADERS = {}
else:
    log(f"✅ API ключ знайдено (довжина: {len(API_KEY_HF)} символів)")
    HEADERS = {"Authorization": f"Bearer {API_KEY_HF}"}


async def classify_image_from_telegram(bot: Bot, telegram_file_id: str) -> str:
    log(f"Отримано запит на класифікацію зображення: {telegram_file_id}")
    try:
        # 1. Отримуємо файл Telegram
        file = await bot.get_file(telegram_file_id)
        image_bytes = await file.download_as_bytearray()
        log(f"Розмір зображення: {len(image_bytes)} байт")

        # 2. Налаштовуємо заголовки
        headers = {
            "Authorization": f"Bearer {API_KEY_HF}",
            "Content-Type": "image/jpeg",
            "Accept-Language": "uk"  # Вказуємо мову відповіді
        }

       # 3. Відправляємо запит до Hugging Face
        log(f"Надсилаємо запит до {HF_API_URL}")
        response = requests.post(
            HF_API_URL,
            headers=headers,  # Використовуємо оновлені заголовки
            data=image_bytes,
            timeout=30  # Додаємо таймаут
        )
        
        # 4. Логуємо відповідь
        log(f"\nСтатус відповіді: {response.status_code}")
        log(f"\nЗаголовки відповіді: {response.headers}")
        log(f"\nТіло відповіді: {response.text[:500]}")

        # 5. Обробляємо відповідь   
        if response.status_code != 200:
            log(f"Помилка API: {response.status_code} - {response.text}")
            return f"❌ Помилка розпізнавання зображення (код {response.status_code})"

        result = response.json()
        log(f"Розпарсена відповідь: {result}")

        # 6. Обробляємо відповідь
        if isinstance(result, list) and len(result) > 0:
            top_prediction = result[0]
            label = top_prediction.get("label")
            log(f"Розпізнано: {label}")
            try:
                translated = GoogleTranslator(source='en', target='uk').translate(label)
                return f"🔍 {translated.capitalize()}"
            except Exception as e:
                log(f"Помилка перекладу: {e}")
                return f"{label.capitalize()}"
            
        return "⚠️ Не вдалося розпізнати зображення"

    except Exception as e:
        log(f"❌ Помилка при класифікації зображення: {e}")
        return "⚠️ Сталася технічна помилка при розпізнаванні зображення."