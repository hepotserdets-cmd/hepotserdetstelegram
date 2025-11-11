from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
import json
import os

# 🔐 Твій токен і чат адміністрації
TOKEN = "8445444619:AAFdR4jF1IQJzEFlL_DsJ-JTxT9nwkwwC58"
ADMIN_CHAT_ID = -1003120877184  # чат адміністраторів (група)
OWNER_ID = 1470389051  # твій особистий айді — тільки ти можеш банити/розбанювати

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 💬 словник для збереження зв’язку повідомлення адміна ↔ користувач
reply_map = {}  # ключ: message_id адміна, значення: user_id

# Файл для збереження банів
BANNED_FILE = "banned.json"
if os.path.exists(BANNED_FILE):
    try:
        with open(BANNED_FILE, "r", encoding="utf-8") as f:
            banned_users = set(json.load(f))
    except Exception:
        banned_users = set()
else:
    banned_users = set()

def save_bans():
    try:
        with open(BANNED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(banned_users), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving bans:", e)

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "🌸 Привет, солнышко!\n\n"
        "Я — бот *Шепот сердец 💌*\n"
        "Можешь написать своё сообщение — и я передам его администраторам.\n"
        "Они обязательно тебе ответят с лучиком тепла ☀️",
        parse_mode="Markdown"
    )

@dp.message(Command("ban"))
async def ban_command(message: Message):
    # команда /ban только от владельца и в админском чате, как reply на сообщение бота, которое хранится в reply_map
    if message.from_user.id != OWNER_ID:
        await message.reply("⛔ У тебя нет прав на эту команду.")
        return
    if message.chat.id != ADMIN_CHAT_ID:
        await message.reply("⛔ Эту команду нужно использовать в админском чате.")
        return
    if not message.reply_to_message:
        await message.reply("❗ Используй /ban в ответ на сообщение (reply) от бота, которое содержит пересланное пользователем сообщение.")
        return

    replied_id = message.reply_to_message.message_id
    if replied_id not in reply_map:
        await message.reply("⚠️ Не удалось найти пользователя по этому reply (возможно это не наше сообщение).")
        return

    user_to_ban = reply_map[replied_id]
    banned_users.add(user_to_ban)
    save_bans()
    # уведомляем в админ чате
    await message.reply(f"✅ Пользователь с ID {user_to_ban} заблокирован.")
    # опционально уведомить самого пользователя (можно закомментировать, если не хочешь уведомлять)
    try:
        await bot.send_message(user_to_ban, "⛔ Ты был заблокирован администрацией и больше не можешь писать в этого бота.")
    except Exception:
        pass

@dp.message(Command("unban"))
async def unban_command(message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("⛔ У тебя нет прав на эту команду.")
        return
    if message.chat.id != ADMIN_CHAT_ID:
        await message.reply("⛔ Эту команду нужно использовать в админском чате.")
        return
    if not message.reply_to_message:
        await message.reply("❗ Используй /unban в ответ на сообщение (reply) от бота, которое содержит пересланное пользователем сообщение.")
        return

    replied_id = message.reply_to_message.message_id
    if replied_id not in reply_map:
        await message.reply("⚠️ Не удалось найти пользователя по этому reply.")
        return

    user_to_unban = reply_map[replied_id]
    if user_to_unban in banned_users:
        banned_users.remove(user_to_unban)
        save_bans()
        await message.reply(f"✅ Пользователь с ID {user_to_unban} разбанен.")
        try:
            await bot.send_message(user_to_unban, "✅ Тебя разблокировали — теперь можно писать боту.")
        except Exception:
            pass
    else:
        await message.reply("ℹ️ Этот пользователь не был в списке забаненных.")

@dp.message(Command("bannedlist"))
async def banned_list(message: Message):
    # только владелец может посмотреть список банов (через админский чат или в личке)
    if message.from_user.id != OWNER_ID:
        await message.reply("⛔ У тебя нет прав на эту команду.")
        return
    if not banned_users:
        await message.reply("Список забаненных пуст.")
        return
    txt = "Забаненные пользователи (ID):\n" + "\n".join(str(x) for x in banned_users)
    await message.reply(txt)

@dp.message()
async def handle_messages(message: Message):
    # Если пишет забаненный пользователь — игнорируем или шлём сообщение
    if message.chat.id != ADMIN_CHAT_ID:
        user_id = message.from_user.id
        if user_id in banned_users:
            # можно тихо игнорировать, или коротко ответить:
            try:
                await message.answer("⛔ Ты заблокирован и не можешь писать в этот бот.")
            except Exception:
                pass
            return

    # 🕊️ Повідомлення від користувача → у чат адмінів
    if message.chat.id != ADMIN_CHAT_ID:
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "без_юзернейма"
        text = f"💬 Сообщение от {username} (ID: {user_id}):\n\n{message.text or '[не текстовое сообщение]'}"
        try:
            sent = await bot.send_message(ADMIN_CHAT_ID, text)
            reply_map[sent.message_id] = user_id
        except Exception as e:
            print("Error sending to admin chat:", e)

    # 🩷 Повідомлення від адміна у reply → користувачу
    elif message.chat.id == ADMIN_CHAT_ID:
        if message.reply_to_message and message.reply_to_message.message_id in reply_map:
            user_id = reply_map[message.reply_to_message.message_id]
            # Якщо користувач в бані, не надсилаємо (але можна повідомити адміну)
            if user_id in banned_users:
                await message.reply("⚠️ Этот пользователь заблокирован — сообщение не отправлено.")
                return
            try:
                await bot.send_message(user_id, f"💌 Ответ администратора:\n\n{message.text}")
            except Exception as e:
                await message.reply(f"❗ Не удалось отправить сообщение пользователю (ID {user_id}).")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
