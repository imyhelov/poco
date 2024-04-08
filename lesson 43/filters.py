from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message):
        member = str(message.from_user.id)
        return member in ["1803073696", ]