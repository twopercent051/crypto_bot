from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode

from tgbot.misc.states import *
from tgbot.keyboards.inline import *
from tgbot.config import load_config
from tgbot.models.mysql_connector import *
from create_bot import bot



config = load_config(".env")
admin_group_id = config.misc.admin_group


async def user_start(message: Message):
    text = [
        'Здравствуйте! Это официальный бот Miner World по обмену криптовалют.'
        'В этом боте вы можете купить или продать USDT, BTC.',
        'На обмен принимаются заявки до 1000$.',
        'Способы оплаты: СБП, Qiwi, Сбербанк, Росбанк.',
        'В случае возникновения проблем нажмите кнопку «поддержка».'

    ]
    keyboard = main_user_keyboard()
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    is_us = await is_user(user_id)
    if is_us == False:
        await create_user(user_id, user_nickname)
    await FSMOffer.home.set()
    await message.answer('\n'.join(text), reply_markup=keyboard)


async def user_home(callback: CallbackQuery):
    text = [
        'Здравствуйте! Это официальный бот Miner World по обмену криптовалют.'
        'В этом боте вы можете купить или продать USDT, BTC.',
        'На обмен принимаются заявки до 1000$.',
        'Способы оплаты: СБП, Qiwi, Сбербанк, Росбанк.',
        'В случае возникновения проблем нажмите кнопку «поддержка».'

    ]
    keyboard = main_user_keyboard()
    # await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await FSMOffer.home.set()
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)


async def show_courses(callback: CallbackQuery):
    text = ['Установленные курсы валют:']
    keyboard = home_keyboard()
    courses = await get_all_courses()
    for cours in courses:
        row = f'<b>{cours[1]}</b>. Цена покупки: {float(cours[3])} ₽, Цена продажи: {float(cours[2])} ₽'
        text.append(row)
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)


async def buy_cripto(callback: CallbackQuery, state: FSMContext):
    text = 'Выберите валюту, которую хотите купить'
    keyboard = coin_keyboard()
    async with state.proxy() as data:
        data['operation'] = 'buy'
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)


async def sell_cripto(callback: CallbackQuery, state: FSMContext):
    text = 'Выберите валюту, которую хотите продать'
    keyboard = coin_keyboard()
    async with state.proxy() as data:
        data['operation'] = 'sell'
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)


async def operation_info(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        operation = data.as_dict()['operation']
    coin = callback.data.upper().split(':')[1]
    op_id, op_text = None, None
    if operation == 'buy':
        op_id = 3
        op_text = 'продаём'
    elif operation == 'sell':
        op_id = 2
        op_text = 'покупаем'
    price_cor = await get_course(coin)
    price = price_cor[op_id]
    print(price)
    async with state.proxy() as data:
        data['price'] = price
        data['coin'] = coin
    text = [
        f'Мы {op_text} <b>{coin}</b> по цене {price} ₽',
        f'Укажите количество <b>{coin}</b>, которое хотите обменять.',
        'Вводить можно как через запятую, так и через точку.',
        'Мы меняем на сумму, не большую эквивалента $1000'
    ]
    # await callback.message.delete()
    await FSMOffer.finish.set()
    # await FSMOffer.net.set()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(' '.join(text))


async def operation_net(message: Message, state: FSMContext):
    try:
        quantity = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            operation = data.as_dict()['operation']
            price = data.as_dict()['price']
        total = round(quantity * float(price), 2)
        text = 'Укажите крипто-сеть'
        keyboard = home_keyboard()
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['quantity'] = quantity
            data['total'] = total
        if operation == 'buy':
            # await FSMOffer.wallet.set()
            await FSMOffer.pay_method.set()
        if operation == 'sell':
            await FSMOffer.pay_details.set()
        await message.answer(text, reply_markup=keyboard)
    except:
        text = 'Вы ввели не число. Попробуйте снова или отмените ввод'
        keyboard = home_keyboard()
        # await message.delete()
        await message.answer(text, reply_markup=keyboard)



async def operation_wallet(message: Message, state: FSMContext):
    crypto_net = message.text
    text = 'Укажите адрес кошелька для начисления Вам криптовалюты'
    keyboard = home_keyboard()
    async with state.proxy() as data:
        data['crypto_net'] = crypto_net
    await FSMOffer.pay_method.set()
    await message.answer(text, reply_markup=keyboard)


async def operation_pay_method(message: Message, state: FSMContext):
    # wallet = message.text
    crypto_net = message.text
    text = [
        'Укажите способ оплаты:',
        'Название банка',
        'СБП (номер телефона) или номер карты'
    ]
    keyboard = home_keyboard()
    # async with state.proxy() as data:
    #     data['wallet'] = wallet
    #     data['pay_details'] = ''
    # await FSMOffer.finish.set()
    # await message.answer('\n'.join(text), reply_markup=keyboard)
    async with state.proxy() as data:
        data['crypto_net'] = crypto_net
        data['wallet'] = ''
    await FSMOffer.finish.set()
    # await message.answer(text, reply_markup=keyboard)
    await message.answer('\n'.join(text), reply_markup=keyboard)




async def operation_pay_details(message: Message, state: FSMContext):
    crypto_net = message.text
    text = 'Укажите реквизиты для перевода рублей'
    keyboard = home_keyboard()
    async with state.proxy() as data:
        data['crypto_net'] = crypto_net
        data['wallet'] = ''
        data['pay_method'] = ''
    await FSMOffer.finish.set()
    await message.answer(text, reply_markup=keyboard)


async def operation_finish(message: Message, state: FSMContext):
    try:
        quantity = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            operation = data.as_dict()['operation']
            coin = data.as_dict()['coin']
            price = data.as_dict()['price']
        total = round(quantity * float(price), 2)
        op_text = ''
        pay_method = ''
        pay_details = ''
        if operation == 'buy':
            op_text = 'покупаете'
            pay_method = message.text
        elif operation == 'sell':
            op_text = 'продаёте'
            pay_details = message.text
        text = [
            f'Вы {op_text} <b>{quantity} {coin}</b> на общую сумму <b>{total} ₽</b>',
            'Подтвердите заявку, и в ближайшее время с Вами свяжется наш сотрудник'
        ]
        keyboard = accept_keyboard()
        user_nickname = f'@{message.from_user.username}' if message.from_user.username is not None else 'Отсутствует'
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['user_username'] = user_nickname
            # data['pay_method'] = pay_method
            # data['pay_details'] = pay_details
        # del_masg = message.message_id - 1
        # await bot.delete_message(chat_id=message.chat.id, message_id=del_masg)
        # await message.delete()
        await message.answer(' '.join(text), reply_markup=keyboard)
    except:
        text = 'Вы ввели не число. Попробуйте снова или отмените ввод'
        keyboard = home_keyboard()
        # await message.delete()
        await message.answer(text, reply_markup=keyboard)



async def operation_accept(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        operation = data.as_dict()['operation']
        coin = data.as_dict()['coin']
        price = data.as_dict()['price']
        user_id = data.as_dict()['user_id']
        user_username = data.as_dict()['user_username']
        total = data.as_dict()['total']
        quantity = data.as_dict()['quantity']
        # crypto_net = data.as_dict()['crypto_net']
        # wallet = data.as_dict()['wallet']
        # pay_method = data.as_dict()['pay_method']
        # pay_details = data.as_dict()['pay_details']

    if operation == 'buy':
        op_text = 'покупку'
        wallet_text = ''
    else:
        op_text = 'продажу'
        admin_wallet = await get_admin_wallet(coin)
        wallet_text = f'Наш кошелёк для внесения криптовалюты: {hcode(admin_wallet[0])}'
    ex_text = []

    user_text = [
        'Спасибо за заявку. В ближайшее время Вам напишет наш сотрудник для уточнения реквизитов',
        wallet_text
    ]
    admin_text = [
        '⚠️⚠️ НОВАЯ ЗАЯВКА ⚠️⚠️',
        f'Вы получили заявку на {op_text}',
        f'<b>Валюта:</b> {coin}',
        f'<b>Цена:</b> {price} ₽',
        f'<b>Количество:</b> {quantity}',
        f'<b>Сумма:</b> {total} ₽',
        # f'<b>Крипто-сеть:</b> {hcode(crypto_net)}',
        f'<b>Юзернейм клиента:</b> {user_username}'
    ]
    # if operation == 'buy':
    #     ex_text = [
    #         f'<b>Кошелёк:</b> {hcode(wallet)}',
    #         f'<b>Способ оплаты:</b> {hcode(pay_method)}',
    #     ]
    # if operation == 'sell':
    #     ex_text = [f'<b>Реквизиты для оплаты:</b> {hcode(pay_details)}']
    admin_text.extend(ex_text)
    admin_keyboard = connect_user_kb(user_id)
    user_keyboard = home_keyboard()
    await create_offer(state)
    await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer('\n'.join(user_text), reply_markup=user_keyboard)
    await bot.send_message(chat_id=admin_group_id, text='\n'.join(admin_text), reply_markup=admin_keyboard)

async def connect_admin(callback: CallbackQuery):
    text = 'Напишите текст ответа'
    keyboard = home_keyboard()
    await FSMConnect.connect.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def answer_admin(message: Message):
    text_admin = 'Сообщение отправлено'
    text_user = [
        '️⚠ СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ: ️⚠',
        f'<i>{message.text}</i>'
    ]
    user_id = message.from_user.id
    answer_keyboard = home_keyboard()
    user_keyboard = connect_user_kb(user_id)
    await bot.send_message(chat_id=admin_group_id, text='\n'.join(text_user), reply_markup=user_keyboard)
    await message.answer(text_admin, reply_markup=answer_keyboard)


async def connect_support(callback: CallbackQuery):
    text = 'Напишите текст вопроса'
    keyboard = home_keyboard()
    await FSMConnect.connect.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)

async def channel(callback: CallbackQuery):
    text = 'Подписывайтесь на наш канал @minerworldex и следите за новостями!'
    keyboard = home_keyboard()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)

async def workout_msg(message: Message):
    text = 'В данный момент у нас нерабочее время. Эта функция станет доступна позже'
    keyboard = home_keyboard()
    await message.answer(text, reply_markup=keyboard)


async def workout_clb(callback: CallbackQuery):
    text = 'В данный момент у нас нерабочее время. Эта функция станет доступна позже'
    keyboard = home_keyboard()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state='*')
    dp.register_message_handler(answer_admin, content_types='text', state=FSMConnect.connect)
    dp.register_message_handler(workout_msg, state='*', is_workout=True)
    dp.register_message_handler(operation_net, content_types='text', state=FSMOffer.net)
    dp.register_message_handler(operation_wallet, content_types='text', state=FSMOffer.wallet)
    dp.register_message_handler(operation_pay_method, content_types='text', state=FSMOffer.pay_method)
    dp.register_message_handler(operation_pay_details, content_types='text', state=FSMOffer.pay_details)
    dp.register_message_handler(operation_finish, content_types='text', state=FSMOffer.finish)


    dp.register_callback_query_handler(user_home, lambda x: x.data == 'home', state='*')
    dp.register_callback_query_handler(user_home, lambda x: x.data == 'cancel', state='*')
    dp.register_callback_query_handler(show_courses, lambda x: x.data == 'course_info', state='*')
    dp.register_callback_query_handler(channel, lambda x: x.data == 'our_channel', state='*')
    dp.register_callback_query_handler(connect_admin, lambda x: x.data.split(':')[0] == 'connect', state='*')
    dp.register_callback_query_handler(connect_support, lambda x: x.data == 'support', state='*')
    dp.register_callback_query_handler(workout_clb, state='*', is_workout=True)
    dp.register_callback_query_handler(buy_cripto, lambda x: x.data == 'buy_crypto', state='*')
    dp.register_callback_query_handler(sell_cripto, lambda x: x.data == 'sell_crypto', state='*')
    dp.register_callback_query_handler(operation_info, lambda x: x.data.split(':')[0] == 'coin', state='*')
    dp.register_callback_query_handler(operation_accept, lambda x: x.data == 'accept', state='*')





