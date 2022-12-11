import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode
from datetime import datetime

from tgbot.config import load_config
from tgbot.keyboards.inline import *
from tgbot.models.db_connector import *
from tgbot.misc.states import *
from create_bot import bot, auto_coins

config = load_config(".env")
admin_group = config.misc.admin_group


async def admin_start_msg(message: Message):
    text = 'Это админ-панель. Тут можно просматривать и менять курсы валют, смотреть статистику и необработанные заявки'
    keyboard = main_admin_keyboard()
    # await message.delete()
    await FSMEditPrice.home.set()
    await message.answer(text, reply_markup=keyboard)


async def admin_start_clb(callback: CallbackQuery):
    text = 'Это админ-панель. Тут можно просматривать и менять курсы валют, смотреть статистику и необработанные заявки'
    keyboard = main_admin_keyboard()
    # await callback.message.delete()
    await FSMEditPrice.home.set()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)

async def admin_get_course(callback: CallbackQuery):
    text = ['Установленные курсы валют:']
    courses = await get_all_courses()
    for cours in courses:
        row = f'<b>{cours[1]}</b>. Цена покупки: {float(cours[2])} ₽, Цена продажи: {float(cours[3])} ₽'
        text.append(row)
    text.append('Выберите валюту для редактирования или вернитесь назад')
    keyboard = coin_keyboard()
    # await callback.message.delete()
    await FSMEditPrice.buy_price.set()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)


async def admin_edit_buy_price(callback: CallbackQuery, state: FSMContext):
    coin = callback.data.split(':')[1].upper()
    price_cor = await get_course(coin, is_money=False)
    price = price_cor[2]
    text = [
        f'Сейчас цена покупки <b>{coin}</b> составляет {price} ₽. Введите нову ценую или нажмите ПРОПУСТИТЬ',
        'Вводить можно как через запятую, так и через точку',
        f'⚠️ВНИМАНИЕ!! Для валют: <b>{auto_coins}</b> указан процент отклонения от официальной цены!'
    ]
    keyboard = miss_keyboard()
    async with state.proxy() as data:
        data['coin'] = coin
    await FSMEditPrice.buy_price.set()
    # await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)

async def admin_edit_sell_price_msg(message: Message, state: FSMContext):
    try:
        price_buy = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            coin = data.as_dict()['coin']
        price_sell_cor = await get_course(coin, is_money=False)
        price_sell = price_sell_cor[3]
        text = [
            f'Новая цена <b>{coin}</b> {price_buy} ₽ сохранена.',
            f'Сейчас цена продажи <b>{coin}</b> составляет {price_sell} ₽. Введите новую цену или нажмите ПРОПУСТИТЬ',
            'Вводить можно как через запятую, так и через точку',
            f'⚠️ВНИМАНИЕ!! Для валют: <b>{auto_coins}</b> указан процент отклонения от официальной цены!'
        ]
        keyboard = miss_keyboard()
        await change_buy_price(coin=coin, price=price_buy)
        await FSMEditPrice.sell_price.set()
        # await message.delete()
        await message.answer(' '.join(text), reply_markup=keyboard)
    except:
        text = 'Вы ввели не число. Попробуйте снова или отмените ввод'
        keyboard = miss_keyboard()
        # await message.delete()
        await message.answer(text, reply_markup=keyboard)


async def admin_edit_price_finish_msg(message: Message, state: FSMContext):
    try:
        price_sell = float(message.text.replace(',', '.'))
        async with state.proxy() as data:
            coin = data.as_dict()['coin']
        text = f'Новая цена <b>{coin}</b> {price_sell} ₽ сохранена.'
        keyboard = home_keyboard()
        await change_sell_price(coin=coin, price=price_sell)
        await FSMEditPrice.sell_price.set()
        # await message.delete()
        await message.answer(text, reply_markup=keyboard)
    except:
        text = 'Вы ввели не число. Попробуйте снова или отмените ввод'
        keyboard = home_keyboard()
        # await message.delete()
        await message.answer(text, reply_markup=keyboard)

async def admin_edit_sell_price_clb(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        coin = data.as_dict()['coin']
    price_sell_cor = await get_course(coin, is_money=False)
    price_sell = price_sell_cor[3]
    text = [
        f'Сейчас цена продажи <b>{coin}</b> составляет {price_sell} ₽. Введите новую цену или нажмите ПРОПУСТИТЬ',
        'Вводить можно как через запятую, так и через точку'
    ]
    keyboard = miss_keyboard()
    await FSMEditPrice.sell_price.set()
    # await callback.message.delete()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def admin_edit_price_finish_clb(callback: CallbackQuery):
    text = 'Спасибо! Изменения сохранены'
    keyboard = home_keyboard()
    await FSMEditPrice.sell_price.set()
    # await callback.message.delete()
    await callback.message.answer(' '.join(text), reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def admin_get_wallet(callback: CallbackQuery):
    text = ['Установленные кошельки:']
    courses = await get_all_courses(is_money=False)
    for cours in courses:
        row = f'Кошелек для <b>{cours[1]}</b> {hcode(cours[4])}'
        text.append(row)
    text.append('Выберите кошелёк для редактирования или вернитесь назад')
    keyboard = coin_keyboard()
    await FSMEditPrice.wallet.set()
    # await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer('\n'.join(text), reply_markup=keyboard)


async def admin_edit_wallet(callback: CallbackQuery, state: FSMContext):
    coin = callback.data.split(':')[1].upper()
    text = f'Введите актуальный кошелек для <b>{coin}</b> или вернитесь на главную'
    keyboard = home_keyboard()
    async with state.proxy() as data:
        data['coin'] = coin
    await FSMEditPrice.wallet.set()
    # await callback.message.delete()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)


async def admin_update_wallet(message: Message, state: FSMContext):
    text = 'Изменения перезаписаны'
    keyboard = home_keyboard()
    async with state.proxy() as data:
        coin = data['coin']
    wallet = message.text
    await update_wallet(coin, wallet)
    await message.answer(text, reply_markup=keyboard)


async def connect_user(callback: CallbackQuery, state: FSMContext):
    text = 'Напишите текст ответа'
    keyboard = home_keyboard()
    user_id = callback.data.split(':')[1]
    async with state.proxy() as data:
        data['user_id'] = user_id
    await FSMConnect.connect.set()
    await callback.message.answer(text, reply_markup=keyboard)
    await bot.answer_callback_query(callback.id)


async def answer_user(message: Message, state: FSMContext):
    text_admin = 'Ответ отправлен'
    text_user = [
        '️⚠ СООБЩЕНИЕ ОТ ОПЕРАТОРА: ️⚠',
        f'<i>{message.text}</i>'
    ]
    keyboard = home_keyboard()
    async with state.proxy() as data:
        user_id = data.as_dict()['user_id']
    user_kb = connect_user_kb(admin_group)
    await bot.send_message(chat_id=user_id, text='\n'.join(text_user), reply_markup=user_kb)
    await message.answer(text_admin, reply_markup=keyboard)


async def get_offers(callback: CallbackQuery):
    text = 'Выберите тип заявок для вывода'
    keyboard = offer_type_keyboard()
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)


async def get_uncompl_offers(callback: CallbackQuery):
    offer_list = await get_offers_req('False')
    if len(offer_list) == 0:
        text = 'У Вас нет необработанных заявок'
        keyboard = home_keyboard()
    else:
        text = 'Список необработанных заявок'
        keyboard = offers_admin_kb(offer_list, 'False')
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)


async def get_compl_offers(callback: CallbackQuery):
    offer_list_prev = await get_offers_req('True')
    offer_list = []
    for offer in offer_list_prev:
        if time.time() - offer[2] < 1209600:
            offer_list.append(offer)
    if len(offer_list) == 0:
        text = 'У Вас нет обработанных заявок за последние 2 недели'
        keyboard = home_keyboard()
    else:
        text = 'Список обработанных заявок. Бот показывает обработанные заявки только за последние 14 дней'
        keyboard = offers_admin_kb(offer_list, 'True')
    await bot.answer_callback_query(callback.id)
    await callback.message.answer(text, reply_markup=keyboard)


async def show_offer(callback: CallbackQuery):
    offer_id = int(callback.data.split(':')[1])
    offer = await get_offer_id(offer_id)
    date = datetime.utcfromtimestamp(offer[2]).strftime('%d-%m-%Y %H:%M')
    if offer[8] == 'False':
        emodji = '⚠️⚠'
    else:
        emodji = '✅✅'
    if offer[3] == 'buy':
        offer_type = 'Покупка'
    else:
        offer_type = 'Продажа'
    ex_text = []
    offer_text = [
        f'{emodji} ЗАЯВКА № {offer_id} {emodji}',
        f'<b>Тип заявки:</b> {offer_type}',
        f'<b>Валюта:</b> {offer[4]}',
        f'<b>Цена:</b> {offer[6]} ₽',
        f'<b>Количество:</b> {offer[5]}',
        f'<b>Сумма:</b> {offer[7]} ₽',
        f'<b>Дата:</b> {date}',
        f'<b>Крипто-сеть:</b> {hcode(offer[9])}'
    ]
    if offer[3] == 'buy':
        ex_text = [
            f'<b>Кошелёк:</b> {hcode(offer[10])}',
            f'<b>Способ оплаты:</b> {hcode(offer[11])}',
        ]
    if offer[3] == 'sell':
        ex_text = [f'<b>Реквизиты для оплаты:</b> {hcode(offer[12])}']
    offer_text.extend(ex_text)
    await bot.answer_callback_query(callback.id)
    if offer[8] == 'False':
        keyboard = uncompl_offer_kb(user_id=offer[1], offer_id=offer_id)
    else:
        keyboard = compl_offer_kb(offer_id)
    await callback.message.answer('\n'.join(offer_text), reply_markup=keyboard)



async def close_offer(callback: CallbackQuery):
    offer_id = int(callback.data.split(':')[1])
    await change_offer_status(offer_id, 'True')
    # await callback.message.delete()
    offer = await get_offer_id(offer_id)
    date = datetime.utcfromtimestamp(offer[2]).strftime('%d-%m-%Y %H:%M')
    emodji = '✅✅'
    if offer[3] == 'buy':
        offer_type = 'Покупка'
    else:
        offer_type = 'Продажа'
    ex_text = []
    offer_text = [
        f'{emodji} ЗАЯВКА № {offer_id} {emodji}',
        f'<b>Тип заявки:</b> {offer_type}',
        f'<b>Валюта:</b> {offer[4]}',
        f'<b>Цена:</b> {offer[6]} ₽',
        f'<b>Количество:</b> {offer[5]}',
        f'<b>Сумма:</b> {offer[7]} ₽',
        f'<b>Дата:</b> {date}',
        f'<b>Крипто-сеть:</b> {hcode(offer[9])}'
    ]
    if offer[3] == 'buy':
        ex_text = [
            f'<b>Кошелёк:</b> {hcode(offer[10])}',
            f'<b>Способ оплаты:</b> {hcode(offer[11])}',
        ]
    if offer[3] == 'sell':
        ex_text = [f'<b>Реквизиты для оплаты:</b> {hcode(offer[12])}']
    offer_text.extend(ex_text)
    await bot.answer_callback_query(callback.id)
    keyboard = compl_offer_kb(offer_id)
    await callback.message.answer('\n'.join(offer_text), reply_markup=keyboard)


async def open_offer(callback: CallbackQuery):
    offer_id = int(callback.data.split(':')[1])
    await change_offer_status(offer_id, 'False')
    # await callback.message.delete()
    offer = await get_offer_id(offer_id)
    date = datetime.utcfromtimestamp(offer[2]).strftime('%d-%m-%Y %H:%M')
    emodji = '⚠️⚠'
    if offer[3] == 'buy':
        offer_type = 'Покупка'
    else:
        offer_type = 'Продажа'
    ex_text = []
    offer_text = [
        f'{emodji} ЗАЯВКА № {offer_id} {emodji}',
        f'<b>Тип заявки:</b> {offer_type}',
        f'<b>Валюта:</b> {offer[4]}',
        f'<b>Цена:</b> {offer[6]} ₽',
        f'<b>Количество:</b> {offer[5]}',
        f'<b>Сумма:</b> {offer[7]} ₽',
        f'<b>Дата:</b> {date}',
        f'<b>Крипто-сеть:</b> {hcode(offer[9])}'
    ]
    if offer[3] == 'buy':
        ex_text = [
            f'<b>Кошелёк:</b> {hcode(offer[10])}',
            f'<b>Способ оплаты:</b> {hcode(offer[11])}',
        ]
    if offer[3] == 'sell':
        ex_text = [f'<b>Реквизиты для оплаты:</b> {hcode(offer[12])}']
    offer_text.extend(ex_text)
    await bot.answer_callback_query(callback.id)
    keyboard = uncompl_offer_kb(user_id=offer[1], offer_id=offer_id)
    await callback.message.answer('\n'.join(offer_text), reply_markup=keyboard)

async def offer_stat(days, closed, opened):
    closed_buy_total = 0
    closed_sell_total = 0
    opened_buy_total = 0
    opened_sell_total = 0
    closed_buy_count = 0
    closed_sell_count = 0
    opened_buy_count = 0
    opened_sell_count = 0
    limit = days * 86400
    for offer in closed:
        if time.time() - offer[2] < limit:
            if offer[3] == 'buy':
                closed_buy_total += offer[7]
                closed_buy_count += 1
            if offer[3] == 'sell':
                closed_sell_total += offer[7]
                closed_sell_count += 1
    for offer in opened:
        if time.time() - offer[2] < limit:
            if offer[3] == 'buy':
                opened_buy_total += offer[7]
                opened_buy_count += 1
            if offer[3] == 'sell':
                opened_sell_total += offer[7]
                opened_sell_count += 1
    result = (closed_buy_total, closed_sell_total, opened_buy_total + closed_buy_total,
              opened_sell_total + closed_sell_total, closed_buy_count, closed_sell_count,
              opened_buy_count + closed_buy_count, opened_sell_count + closed_sell_count)
    return result


async def get_statistic(callback: CallbackQuery):
    closed_offers = await get_offers_req('True')
    opened_offers = await get_offers_req('False')
    days = [1, 7, 30]
    for day in days:
        offer_result = await offer_stat(day, closed_offers, opened_offers)
        timestamp = time.time() - (day * 86400)
        user_result = await user_count(timestamp)
        day_text = [
            f'За последние {day} дней:',
            f'Зарегистрировались {user_result} новых пользователей',
            f'Получили {offer_result[7]} заявок на продажу {offer_result[3]} ₽',
            f'Получили {offer_result[6]} заявок на покупку {offer_result[2]} ₽',
            f'Завершили {offer_result[5]} заявок на продажу {offer_result[1]} ₽',
            f'Завершили {offer_result[4]} заявок на покупку {offer_result[0]} ₽',
        ]
        keyboard = home_keyboard()
        await callback.message.answer('\n'.join(day_text), reply_markup=keyboard)
        await bot.answer_callback_query(callback.id)


async def dump_db(callback: CallbackQuery):
    dumper()
    time.sleep(3)
    doc_path = f'{os.getcwd()}/backupdatabase.sql'
    await bot.send_document(chat_id=admin_group, document=open(doc_path, 'rb'))
    await bot.answer_callback_query(callback.id)




def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start_msg, state="*", chat_id=admin_group, commands='start')
    dp.register_message_handler(admin_edit_sell_price_msg, state=FSMEditPrice.buy_price, content_types='text',
                                chat_id=admin_group)
    dp.register_message_handler(admin_edit_price_finish_msg, state=FSMEditPrice.sell_price, content_types='text',
                                chat_id=admin_group)
    dp.register_message_handler(answer_user, state=FSMConnect.connect, content_types='text', chat_id=admin_group)
    dp.register_message_handler(admin_update_wallet, state=FSMEditPrice.wallet, content_types='text',
                                chat_id=admin_group)



    dp.register_callback_query_handler(admin_start_clb, lambda x: x.data == 'home', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(admin_get_course, lambda x: x.data == 'edit_course', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(admin_edit_buy_price, lambda x: x.data.split(':')[0] == 'coin',
                                       state=FSMEditPrice.buy_price, chat_id=admin_group)
    dp.register_callback_query_handler(admin_edit_sell_price_clb, lambda x: x.data == 'miss',
                                       state=FSMEditPrice.buy_price, chat_id=admin_group)
    dp.register_callback_query_handler(admin_edit_price_finish_clb, lambda x: x.data == 'miss',
                                       state=FSMEditPrice.sell_price, chat_id=admin_group)
    dp.register_callback_query_handler(connect_user, lambda x: x.data.split(':')[0] == 'connect', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(get_offers, lambda x: x.data == 'get_offers', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(get_uncompl_offers, lambda x: x.data == 'get_uncompl', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(get_compl_offers, lambda x: x.data == 'get_compl', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(show_offer, lambda x: x.data.split(':')[0] == 'offer', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(close_offer, lambda x: x.data.split(':')[0] == 'close', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(open_offer, lambda x: x.data.split(':')[0] == 'open', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(get_statistic, lambda x: x.data.split(':')[0] == 'get_stat', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(dump_db, lambda x: x.data == 'dump_db', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(admin_get_wallet, lambda x: x.data == 'edit_wallet', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(admin_edit_wallet, lambda x: x.data.split(':')[0] == 'coin',
                                       state=FSMEditPrice.wallet, chat_id=admin_group)


