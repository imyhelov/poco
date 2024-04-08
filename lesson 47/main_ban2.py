import logging
import time
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import ParseMode
from aiogram.utils import executor
from config import TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


class IsGroup(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        )


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message):
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin()

# @dp.message_handler()
# async def delete_message(message: types.Message):
#     time.sleep(2)
#     await message.delete()


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand('set_photo', 'Установить фото в группе'),
        types.BotCommand('set_title', 'Установить название группы'),
        types.BotCommand('set_descriprtion', 'Установить описание группы'),
        types.BotCommand('Roman', 'Режим чтения'),
        types.BotCommand('UnRoman', 'Отключить режим чтения'),
        types.BotCommand('ban', 'Забанить пользователя'),
        types.BotCommand('unban', 'Разбанить пользователя')
    ])


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    await message.reply(f'Привет {message.new_chat_members[0].full_name}!\nВ нашем чате можно общаться\nРугаться нельзя, ато будет ай ай ай')

# @dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
# async def banned_member(message: types.Message):
#     await message.reply(f'{message.left_chat_member.full_name} был удален из чата польвозателем {message.from_user.full_name}\n'
#                         f'Прощай, дружице!')


@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    if message.left_chat_member.id == message.from_user.id:
        await message.answer(f'{message.left_chat_member.full_name} вышел из чата\nПрощай, Дружище!')
    else:
        await message.reply(f'{message.left_chat_member.full_name} был удален из чата пользователем {message.from_user.full_name}')


@dp.message_handler(IsGroup(), commands='ban')
async def ban_user(message: types.Message):
    try:
        if not message.reply_to_message:
            await message.answer('not')
            return

        member = message.reply_to_message.from_user
        member_id = member.id
        chat_id = message.chat.id
        await message.chat.kick(user_id=member_id)
        await message.reply(f"ПОльзователь {member.full_name} был забанен")

    except Exception:
        print('Ошибка')
        #await message.reply(f"Пользователь {member.full_name} не был забанен")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)