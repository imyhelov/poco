import asyncio
import datetime
import io
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils.exceptions import BadRequest

from config import TOKEN

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message):
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin()


class IsGroup(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        )


dp.filters_factory.bind(IsGroup)


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand('set_photo', 'установить фото в группе'),
        types.BotCommand('set_title', 'установить название'),
        types.BotCommand('ro', 'read only'),
        types.BotCommand('unro', 'read only off'),
    ])


@dp.message_handler(IsGroup(), commands="set_photo")
async def set_new_photo(message: types.Message):
    source_message = message.reply_to_message
    photo = source_message.photo[-1]
    photo = await photo.download(destination=io.BytesIO())
    input_file = types.InputFile(path_or_bytesio=photo)
    await message.chat.set_photo(photo=input_file)


@dp.message_handler(IsGroup(), commands='ban')
async def ban_user(message: types.Message):
    global member
    try:
        if not message.reply_to_message:
            await message.answer('fgh')
            return

        member = message.reply_to_message.from_user
        member_id = member.id
        chat_id = message.chat.id
        await message.chat.kick(user_id=member_id)
        await message.reply(f"пользователь {member.full_name} был забанен")

    except Exception:
        print('Ошибка')
        await message.reply(f"пользователь {member.full_name} был забанен")


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    await message.reply(f"Привет{message.new_chat_members[0].full_name}, в нашей группе запрещеные политичиские споры")


@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def ban_member(message: types.Message):
    await message.reply(f"Пользователь {message.left_chat_member.full_name}, покинул чат")


@dp.message_handler(IsGroup(), commands='unban')
async def unban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    await message.chat.unban(user_id=member_id)
    await message.reply(f'Пользователь {member.full_name} был разбанен')
    service_message = await message.reply('Сообщение удалится через 5 секунд')
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


dp.filters_factory.bind(AdminFilter)


@dp.message_handler(IsGroup(), AdminFilter(), commands=['ro'])
async def read_only_mode(message: types.Message):
   if not message.reply_to_message:
      await message.answer('reply')
      return
   member = message.reply_to_message.from_user
   member_id = member.id
   chat_id = message.chat.id
   time = 1
   reason = 'спам'
   until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)
   ReadOnlyPermisson = types.ChatPermissions(
         can_send_messages=False,
         can_send_media_messages=False,
         can_send_polls=False,
         can_pin_messages=False,
         can_invite_users=True,
         can_change_info=False,
         can_add_web_page_previews=False,
      )

   try:
      await bot.restrict_chat_member(chat_id, user_id=member_id, permissions=ReadOnlyPermisson, until_date=until_date)
      response_message = await message.answer(f'Пользователю {member.get_mention(as_html=True)} запрещено писать сообшения в течении {time}минут, по причине {reason}\nЭто сообщение удалится за 5 минут')
      await asyncio.sleep(300)
      await response_message.delete()

   except BadRequest as e:
      logging.error(f'Failed {e}')
      await message.answer(f'Не получилось замьючить по причине{str(e)}')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
