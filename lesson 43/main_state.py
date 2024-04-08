from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

availiable_food_names = ['суши', "спагетти", "хачапури"]
availiable_food_sizes = ['маленькую', "среднюю", "большую"]

class OrderFood(StatesGroup):
    waiting_for_food_name = State()
    waiting_for_food_size = State()

async def food_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in availiable_food_names:
        keyboard.add(name)
    await message.answer('Выберите блюдо:', reply_markup=keyboard)
    await OrderFood.waiting_for_food_name.set()


async def food_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in availiable_food_names:
        await message.answer('Пожалуйста, выберите блюдо, используя клавиатуру ниже')
        return
    await state.update_data(chosen_food=message.text.lower())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in availiable_food_sizes:
        keyboard.add(size)
        await message.answer('Теперь выбери размер порции:', reply_markup=keyboard)
        await OrderFood.next()


async def food_size_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in availiable_food_sizes:
        await message.answer('Пожалуйста, выберите размер порции')
        return
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {message.text.lower()} порцию {user_data['chosen_food']}\n"
                         f"Попробуйте теперь выбрать и напитки: /drinks", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_food(dp: Dispatcher):
    dp.register_message_handler(food_start, commands='food', state='*')
    dp.register_message_handler(food_chosen, state=OrderFood.waiting_for_food_name)
    dp.register_message_handler(food_size_chosen, state=OrderFood.waiting_for_food_size)


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выберите, что хотите заказать: напитки(/drinks) или блюда (/food).',
                         reply_markup=types.ReplyKeyboardMarkup())



async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отмены',
                         reply_markup=types.ReplyKeyboardMarkup())


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start', state='*')
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(cmd_cancel, lambda message: message.text.lower() == 'отмена', state="*")


def main():
    register_handlers_common(dp)
    register_handlers_food(dp)
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()