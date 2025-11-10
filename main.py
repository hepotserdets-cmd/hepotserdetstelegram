import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.getenv("TOKEN") or "8445444619:AAFdR4jF1IQJzEFlL_DsJ-JTxT9nwkwwC58"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or "-1003120877184")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словник для зв’язку між адмінським повідомленням і користувачем
reply_map = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет!\n"
        "Рад тебя видеть! 💫\n"
        "Я — бот *Шепот сердец 💌*\n\n"
        "Можешь написать своё сообщение — администратор скоро тебе ответит.",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_messages(message: types.Message):
    # Якщо пише користувач — пересилаємо в адмін-чат
    if message.chat.id != ADMIN_CHAT_ID:
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "без_юзернейма"
        text = f"📩 Сообщение от {username} (ID: {user_id}):\n\n{message.text or '[не текстовое сообщение]'}"
        sent = await bot.send_message(ADMIN_CHAT_ID, text)
        reply_map[sent.message_id] = user_id

    # Якщо пише адмін у reply
    elif message.chat.id == ADMIN_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.message_id in reply_map:
            user_id = reply_map[message.reply_to_message.message_id]
            await bot.send_message(user_id, f"💌 Ответ админа:\n\n{message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
