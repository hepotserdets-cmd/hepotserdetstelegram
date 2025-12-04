from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import threading
from aiohttp import web

# 🔐 Твій токен і чат адміністрації
TOKEN = "8291867377:AAGqd4UAVY4gU3zVR5YevZSb1Nly6j6-UDY"
ADMIN_CHAT_ID = -1003120877184  # чат адміністраторів
MY_ID = 1470389051  # твій особистий ID для команди /ban

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 💬 словник для збереження зв’язку повідомлення адміна ↔ користувач
reply_map = {}  # ключ: message_id адміна, значення: user_id
banned_users = set()  # заблоковані користувачі

# ==================== Telegram Bot ====================

@dp.message(Command("start"))
async def start_command(message: Message):
    if message.from_user.id in banned_users:
        return  # не відповідаємо заблокованим
    await message.answer(
        "🌸 Привет, солнышко!\n\n"
        "Я — бот *Шепот сердец 💌*\n"
        "Можешь написать своё сообщение — и я передам его администраторам.\n"
        "Они обязательно тебе ответят с лучиком тепла ☀️",
        parse_mode="Markdown"
    )

@dp.message(Command("ban"))
async def ban_command(message: Message):
    if message.from_user.id != MY_ID:
        return
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        banned_users.add(user_id)
        await message.answer(f"🚫 Пользователь {user_id} заблокирован.")

@dp.message(Command("banned"))
async def list_banned(message: Message):
    if message.from_user.id != MY_ID:
        return
    if not banned_users:
        await message.answer("Нет заблокированных пользователей.")
    else:
        text = "Заблокированные пользователи:\n" + "\n".join(str(u) for u in banned_users)
        await message.answer(text)

@dp.message()
async def handle_messages(message: Message):
    if message.from_user.id in banned_users:
        return  # не відповідаємо заблокованим

    # 🕊️ Повідомлення від користувача → у чат адмінів
    if message.chat.id != ADMIN_CHAT_ID:
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "без_юзернейма"
        text = f"💬 Сообщение от {username} (ID: {user_id}):\n\n{message.text or '[не текстовое сообщение]'}"
        sent = await bot.send_message(ADMIN_CHAT_ID, text)
        reply_map[sent.message_id] = user_id

    # 🩷 Повідомлення від адміна у reply → користувачу
    elif message.chat.id == ADMIN_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.message_id in reply_map:
            user_id = reply_map[message.reply_to_message.message_id]
            await bot.send_message(user_id, f"💌 Ответ администратора:\n\n{message.text}")

# ==================== Web server для Render ====================

async def handle(request):
    return web.Response(text="Bot is running!")

def run_web():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    web.run_app(app, port=8000)

# ==================== Main ====================

if __name__ == "__main__":
    # запуск веб-сервера в окремому потоці
    t = threading.Thread(target=run_web)
    t.start()
    # запуск Telegram бота
    asyncio.run(dp.start_polling(bot))
