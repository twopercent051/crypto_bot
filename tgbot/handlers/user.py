from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from tgbot.misc.states import *
from tgbot.keyboards import reply
from tgbot.keyboards.inline import *
from tgbot.config import load_config
from tgbot.models.db_connector import *
from create_bot import bot



config = load_config(".env")
admin_group_id = config.misc.admin_group


def mute(message: Message):
    pass


async def user_start(message: Message):
    text = [
        'Здравствуйте! Это приветственное сообщение, его нужно отредактировать. Тут можно писать <b>жирным</b>,',
        '<i>курсивом</i>, <u>подчёркнутым</u>, <b><i>а также любыми</i></b> <u><i>комбинациями</i></u>. Ещё можно',
        'добавить эмодзи 🇬🇧.',
        '\n',
        'А теперь нажмите на интересующую кнопку!'
    ]
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    is_us = await is_user(user_id)
    if is_us == False:
        await create_user(user_id, user_nickname)
        await FSMOffer.home.set()
    await message.answer(''.join(text), reply_markup=main_user_keyboard)


async def user_home(callback: CallbackQuery):
    text = 'ГЛАВНОЕ МЕНЮ ПОЛЬЗОВАТЕЛЯ'
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await FSMOffer.home.set()
    await callback.message.answer(text, reply_markup=main_user_keyboard)


async def show_courses(callback: CallbackQuery):
    text = ['Установленные курсы валют:']
    courses = await get_all_courses()
    for cours in courses:
        row = f'<b>{cours[1]}</b>. Цена покупки: {float(cours[2])} ₽, Цена продажи: {float(cours[3])} ₽'
        text.append(row)
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer('\n'.join(text), reply_markup=home_keyboard)


async def buy_cripto(callback: CallbackQuery, state: FSMContext):
    text = 'Выберите валюту, которую хотите купить'
    async with state.proxy() as data:
        data['operation'] = 'buy'
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=coin_keyboard)


async def sell_cripto(callback: CallbackQuery, state: FSMContext):
    text = 'Выберите валюту, которую хотите продать'
    async with state.proxy() as data:
        data['operation'] = 'sell'
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=coin_keyboard)


async def operation_info(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        operation = data.as_dict()['operation']
    coin = callback.data.upper().split(':')[1]
    if operation == 'buy':
        op_id = 2
        op_text = 'продаём'
    elif operation == 'sell':
        op_id = 3
        op_text = 'покупаем'
    price_cor = await get_course(coin)
    price = price_cor[op_id]
    async with state.proxy() as data:
        data['price'] = price
        data['coin'] = coin
    text = [
        f'Мы {op_text} <b>{coin}</b> по цене {price} ₽',
        f'Укажите количество <b>{coin}</b>, которое хотите обменять.',
        'Вводить можно как через запятую, так и через точку.',
        'Мы меняем на сумму, не большую эквивалента $1000'
    ]
    await callback.message.delete()
    await FSMOffer.operation.set()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(' '.join(text))


async def operation_finish(message: Message, state: FSMContext):
    try:
        quantity = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            operation = data.as_dict()['operation']
            coin = data.as_dict()['coin']
            price = data.as_dict()['price']
        total = float(quantity) * float(price)
        if operation == 'buy':
            op_text = 'покупаете'
        elif operation == 'sell':
            op_text = 'продаёте'
        text = [
            f'Вы {op_text} <b>{quantity} {coin}</b> на общую сумму <b>{total} ₽</b>',
            'Подтвердите заявку, и в ближайшее время с Вами свяжется наш сотрудник'
        ]
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['quantity'] = quantity
            data['total'] = total
        del_masg = message.message_id - 1
        await bot.delete_message(chat_id=message.chat.id, message_id=del_masg)
        await message.delete()
        await message.answer(' '.join(text), reply_markup=accept_keyboard)
    except:
        text = 'Вы ввели не число. Попробуйте снова или отмените ввод'
        await message.delete()
        await message.answer(text, reply_markup=home_keyboard)

async def operation_accept(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        operation = data.as_dict()['operation']
        coin = data.as_dict()['coin']
        price = data.as_dict()['price']
        user_id = data.as_dict()['user_id']
        total = data.as_dict()['total']
        quantity = data.as_dict()['quantity']
    if operation == 'buy':
        op_text = 'покупку'
    else:
        op_text = 'продажу'
    user_text = 'Спасибо за заявку. В ближайшее время Вам напишет наш сотрудник для уточнения реквизитов'
    admin_text = [
        '⚠️⚠️ НОВАЯ ЗАЯВКА ⚠️⚠️',
        f'Вы получили заявку на {op_text}',
        f'<b>Валюта:</b> {coin}',
        f'<b>Цена:</b> {price} ₽',
        f'<b>Количество:</b> {quantity}',
        f'<b>Сумма:</b> {total} ₽'
    ]
    keyboard = connect_user_kb(user_id)
    await create_offer(state)
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(user_text, reply_markup=home_keyboard)
    await bot.send_message(chat_id=admin_group_id, text='\n'.join(admin_text), reply_markup=keyboard)

async def connect_admin(callback: CallbackQuery):
    text = 'Напишите текст ответа'
    await FSMConnect.connect.set()
    await callback.message.answer(text, reply_markup=home_keyboard)
    await bot.answer_callback_query(callback.id)


async def answer_admin(message: Message, state: FSMContext):
    text_admin = 'Сообщение отправлено'
    text_user = [
        '️⚠ СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ: ️⚠',
        f'<i>{message.text}</i>'
    ]
    user_id = message.from_user.id
    # async with state.proxy() as data:
    #     user_id = data.as_dict()['user_id']
    user_kb = connect_user_kb(user_id)
    await bot.send_message(chat_id=admin_group_id, text='\n'.join(text_user), reply_markup=user_kb)
    await message.answer(text_admin, reply_markup=home_keyboard)


async def connect_support(callback: CallbackQuery):
    text = 'Напишите текст вопроса'
    await FSMConnect.connect.set()
    await callback.message.answer(text, reply_markup=home_keyboard)
    await bot.answer_callback_query(callback.id)



def register_user(dp: Dispatcher):
    dp.register_message_handler(mute, chat_id=admin_group_id)
    dp.register_message_handler(user_start, commands=["start"], state='*')
    dp.register_message_handler(operation_finish, content_types='text', state=FSMOffer.operation)
    dp.register_message_handler(answer_admin, content_types='text', state=FSMConnect.connect)

    dp.register_callback_query_handler(user_home, lambda x: x.data == 'home', state='*')
    dp.register_callback_query_handler(user_home, lambda x: x.data == 'cancel', state='*')
    dp.register_callback_query_handler(show_courses, lambda x: x.data == 'course_info', state='*')
    dp.register_callback_query_handler(buy_cripto, lambda x: x.data == 'buy_crypto', state='*')
    dp.register_callback_query_handler(sell_cripto, lambda x: x.data == 'sell_crypto', state='*')
    dp.register_callback_query_handler(operation_info, lambda x: x.data.split(':')[0] == 'coin', state='*')
    dp.register_callback_query_handler(connect_admin, lambda x: x.data.split(':')[0] == 'connect', state='*')
    dp.register_callback_query_handler(operation_accept, lambda x: x.data == 'accept', state='*')
    dp.register_callback_query_handler(connect_support, lambda x: x.data == 'support', state='*')



