from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from crud_functions_ import initiate_db, add_product, get_all_products, add_user, is_included


api = ""
bot = Bot(token=api)

dp = Dispatcher(bot, storage=MemoryStorage())

initiate_db()
add_product("Продукт 1", "Описание 1", 100)
add_product("Продукт 2", "Описание 2", 200)
add_product("Продукт 3", "Описание 3", 300)
add_product("Продукт 4", "Описание 4", 400)
products = get_all_products()

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать"), KeyboardButton(text="Информация")],
        [KeyboardButton(text="Купить"), KeyboardButton(text="Регистрация")]
    ], resize_keyboard=True
)

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()



inline_kb = InlineKeyboardMarkup()
inline_button_calories = InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")
inline_button_formulas = InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
inline_kb.add(inline_button_calories, inline_button_formulas)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=["start"])
async def start_message(message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup=start_menu)

@dp.message_handler(text = "Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит): ")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    if is_included(username):
        await message.answer("Пользователь существует, введите другое имя")
        return
    await state.update_data(username=username)
    await message.answer("Введите свой email:")
    await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    age = int(message.text)
    data = await state.get_data()
    username = data["username"]
    email = data["email"]
    add_user(username, email, age)
    await message.answer("Регистрация прошла успешно!")
    await RegistrationState.age.set()
    await state.finish()



@dp.message_handler(text = "Информация")
async def inform(message):
    await message.answer("Информация о боте!")

@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    formulas_message = (
        "Формула Миффлина-Сан Жеора:"
        "Для мужчин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5"
        "Для женщин: BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formulas_message, reply_markup=inline_kb)
    await call.answer()

@dp.callback_query_handler(text="calories")
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data["age"])
    growth = int(data["growth"])
    weight = int(data["weight"])

    calories_man = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_woman = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий для мужчин: {calories_man:.2f} ккал")
    await message.answer(f"Ваша норма калорий для женщин: {calories_woman:.2f} ккал")

    await state.finish()

@dp.message_handler(text="Купить")
async def get_buying_list(message):
    products = get_all_products()
    image_files = ["files/5.jpg", "files/6.jpg", "files/7.jpg", "files/8.jpg"]

    inline_button_products = InlineKeyboardMarkup()
    button_row = [
        InlineKeyboardButton(text=product[1],
    callback_data=f"product_buying:{product[0]}")
        for product in products
    ]
    inline_button_products.row(*button_row)


    for i, (product_id, title, description, price) in enumerate(products):
        product_message = f"Название: {title} | Описание: {description} | Цена: {price}"
        await message.answer(product_message)

        if i < len(image_files):
            with open(image_files[i], "rb") as img:
                await message.answer_photo(img)

    await message.answer("Выберите продукт для покупки:", reply_markup=inline_button_products)

@dp.callback_query_handler(lambda call: call.data.startswith("product_buying:"))
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.message_handler()
async def all_message(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)