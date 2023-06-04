import os
import random
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token='BOT_TOKEN')
dp = Dispatcher(bot)

keyboard_inline = InlineKeyboardMarkup()
button1 = InlineKeyboardButton(text="📜 Kurallar 📜", callback_data="kurallar")
button2 = InlineKeyboardButton(text="🎥 Video Takas Et 📷", callback_data="video_takas_et")
keyboard_inline.add(button1, button2)

keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard1.add("📜 Kurallar 📜", "🎥 Video Takas Et 📷")

waiting_for_video = {}  # Kullanıcıların video göndermesini beklemek için kullanılacak bir sözlük

ADMIN_KEY = "admin123"  # Admin anahtar kelimesi

@dp.message_handler(commands=['random'])
async def random_answer(message: types.Message):
    await message.reply("Select a range:", reply_markup=keyboard_inline)

@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.reply("Merhaba Video Takas Botuna Hoşgeldiniz Lütfen Video Göndermeden Önce Kuralları Okuyun", reply_markup=keyboard1)

@dp.callback_query_handler(text=["kurallar", "video_takas_et"])
async def button_click(call: types.CallbackQuery):
    if call.data == "kurallar":
        await call.message.reply("Videonunuz gönderin")
    elif call.data == "video_takas_et":
        user_id = call.from_user.id
        if user_id in waiting_for_video:
            await call.message.reply("Karşı tarafın videoyu göndermesini bekliyorum...")
        else:
            video_folder = 'videos'
            video_files = os.listdir(video_folder)
            random_video_file = random.choice(video_files)

            waiting_for_video[user_id] = random_video_file

            await call.message.reply("Karşı tarafın videoyu göndermesini iste")

    await call.answer()

@dp.message_handler(content_types=types.ContentTypes.VIDEO)
async def receive_video(message: types.Message):
    user_id = message.from_user.id
    if user_id in waiting_for_video:
        video_path = os.path.join('videos', waiting_for_video[user_id])

        # Kontrol etmek için önceki video dosyasının özelliklerini al
        previous_video_properties = waiting_for_video[user_id]

        # Şu anki video dosyasının özelliklerini al
        current_video_properties = f"{message.video.file_unique_id}_{message.video.file_size}"

        # Önceki ve şu anki video özelliklerini karşılaştır
        if previous_video_properties == current_video_properties:
            await message.reply("Aynı videoyu birden fazla kez gönderemezsin!")
            return

        with open(video_path, 'rb') as video_file:
            await bot.send_video(message.chat.id, video_file)

        # Gönderilen videoyu "gönderilen videolar" klasörüne kaydet
        video_save_path = os.path.join('gönderilen videolar', f"{message.from_user.username}_{message.from_user.first_name}_{user_id}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4")
        await message.video.download(video_save_path)

        del waiting_for_video[user_id]
    else:
        await message.reply("Beklenmedik bir video geldi!")

@dp.message_handler(commands=['admin'])
async def admin_command(message: types.Message):
    if message.text.split()[1] == ADMIN_KEY:
        keyboard_admin = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard_admin.add("1️⃣ Videos Klasöründeki Videoları Gönder", "2️⃣ Gönderilen Videolar Klasöründeki Videoları Gönder")

        await message.reply("Hangi videoları göndermek istersiniz?", reply_markup=keyboard_admin)
    else:
        await message.reply("Invalid admin key.")

@dp.message_handler()
async def kb_answer(message: types.Message):
    if message.text == '📜 Kurallar 📜':
        await message.reply("KURALARI YAZIN")
    elif message.text == '🎥 Video Takas Et 📷':
        user_id = message.from_user.id
        if user_id in waiting_for_video:
            await message.reply("video göndermenizi bekliyorum...")
        else:
            video_folder = 'videos'
            video_files = os.listdir(video_folder)
            random_video_file = random.choice(video_files)

            waiting_for_video[user_id] = random_video_file

            await message.reply("lütfen takas edilecek videoyu gönderin")

    elif message.text == '1️⃣ Videos Klasöründeki Videoları Gönder':
        video_folder = 'videos'
        video_files = os.listdir(video_folder)
        if video_files:
            for video_file in video_files:
                with open(os.path.join(video_folder, video_file), 'rb') as video:
                    await bot.send_video(message.chat.id, video)
        else:
            await message.reply("No videos found in the 'videos' folder.")

    elif message.text == '2️⃣ Gönderilen Videolar Klasöründeki Videoları Gönder':
        video_folder = 'gönderilen videolar'
        video_files = os.listdir(video_folder)
        if video_files:
            for video_file in video_files:
                with open(os.path.join(video_folder, video_file), 'rb') as video:
                    await bot.send_video(message.chat.id, video)
        else:
            await message.reply("No videos found in the 'gönderilen videolar' folder.")

    elif message.reply_to_message and message.reply_to_message.video and message.text.startswith("Admin sil"):
        user_id = message.reply_to_message.from_user.id
        if message.text.split()[2] == ADMIN_KEY:
            video_path = os.path.join('gönderilen videolar', f"{user_id}.mp4")
            if os.path.exists(video_path):
                os.remove(video_path)
                await message.reply("Video successfully deleted.")
            else:
                await message.reply("Video not found.")
        else:
            await message.reply("Invalid admin key.")

    else:
        await message.reply(f"Your message is: {message.text}")

@dp.message_handler()
async def log_user_info(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    phone_number = message.from_user.phone_number if message.from_user.phone_number else "N/A"

    log_message = f"User Info: ID={user_id}, Username={username}, Full Name={full_name}, Phone Number={phone_number}\n"

    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_message)

executor.start_polling(dp)
