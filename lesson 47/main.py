import logging
import time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TOKEN
API_TOKEN = TOKEN
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def del_m(message: types.Message):
    time.sleep(1)
    await message.delete()

async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand('set_photo',' Установить фото в группе'),
        types.BotCommand('set_title', 'Установить название группы'),
        types.BotCommand('set_description', 'Установить описание группы'),
        types.BotCommand('Roman','Режим только чтение'),
        types.BotCommand('UnRoman', "Отключить режим только чтения"),
        types.BotCommand('ban', 'Забанить пользователя'),
        types.BotCommand('unban', 'Разбанить')
    ])


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    await message.reply(f"Привет{message.new_chat_members[0].full_name}. В нашем чате можно все хорошее, все плохое нельзя")


# @dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
# async def banned_member(message: types.Message):
#     await message.reply(
#         f'{message.left_chat_member.full_name} был удален из чата пользователем {message.from_user.full_name}'
#     )

@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    if message.left_chat_member.id == message.from_user.id:
        await message.answer(f'{message.left_chat_member.full_name} вышел из чата')
    else:
        await message.reply(f'{message.left_chat_member.full_name} был удален из чата пользователем{message.from_user.full_name}')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
