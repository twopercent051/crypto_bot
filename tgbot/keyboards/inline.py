from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.models import db_connector
import time

coins = db_connector.get_coins()


buy_button = InlineKeyboardButton(text='🔲 Купить крипту 🔲', callback_data='buy_crypto')
sell_button = InlineKeyboardButton(text='🔳 Продать крипту 🔳', callback_data='sell_crypto')
course_info_button = InlineKeyboardButton(text='❔ Посмотреть курс ❔', callback_data='course_info')
our_channel_button = InlineKeyboardButton(text='📱 Наш канал 📱', callback_data='our_channel')
support_button = InlineKeyboardButton(text='🆘 Поддержка 🆘', callback_data='support')

edit_course_button = InlineKeyboardButton(text='Редактировать курс', callback_data='edit_course')
get_stat_button = InlineKeyboardButton(text='Статистика', callback_data='get_stat')
get_offers_button = InlineKeyboardButton(text='Заявки', callback_data='get_offers')
dump_button = InlineKeyboardButton(text='Дамп базы', callback_data='dump_db')

get_uncompl_button = InlineKeyboardButton(text='❌Незавершённые❌', callback_data='get_uncompl')
get_compl_button = InlineKeyboardButton(text='✅Завершённые✅', callback_data='get_compl')


back_button = InlineKeyboardButton(text='⬅️⬅️ НАЗАД ⬅️⬅️', callback_data='back')
home_button = InlineKeyboardButton(text='🏠🏠 ДОМОЙ 🏠🏠', callback_data='home')
miss_button = InlineKeyboardButton(text='❌❌ ПРОПУСТИТЬ ❌❌', callback_data='miss')
accept_button = InlineKeyboardButton(text='✅✅ ПОДТВЕРДИТЬ ✅✅', callback_data='accept')
cancel_button = InlineKeyboardButton(text='❌❌ ОТМЕНИТЬ ❌❌', callback_data='cancel')


main_user_keyboard = InlineKeyboardMarkup(row_width=2).add(buy_button, sell_button, course_info_button,
                                                           our_channel_button, support_button)
main_admin_keyboard = InlineKeyboardMarkup(row_width=1).add(edit_course_button, get_stat_button, get_offers_button,
                                                            dump_button)
miss_keyboard = InlineKeyboardMarkup(row_width=1).add(miss_button, home_button)
home_keyboard = InlineKeyboardMarkup(row_width=1).add(home_button)
accept_keyboard = InlineKeyboardMarkup(row_width=1).add(accept_button, cancel_button)
offer_type_keyboard = InlineKeyboardMarkup(row_width=1).add(get_uncompl_button, get_compl_button)




coin_keyboard = InlineKeyboardMarkup(row_width=2)
coins = db_connector.get_coins()
for coin in coins:
    coin_button = InlineKeyboardButton(text=coin[0], callback_data=f'coin:{coin[0].lower()}')
    coin_keyboard.add(coin_button)
coin_keyboard.add(home_button)

def connect_user_kb(user_id):
    connect_button = InlineKeyboardButton(text='📞📞 ОТВЕТИТЬ 📞📞', callback_data=f'connect:{user_id}')
    connect_keyboard = InlineKeyboardMarkup(row_width=1).add(connect_button)
    return connect_keyboard

def offers_admin_kb(offer_list, is_completed):
    if is_completed == 'True':
        emodji = '✅ '
    else:
        emodji = '❌'
    for offer in offer_list:
        offer_id = offer[0]
        offer_button = InlineKeyboardButton(text=f'{emodji} --ID {offer_id}-- {emodji}',
                                            callback_data=f'offer:{offer_id}')
        offer_keyboard = InlineKeyboardMarkup(row_width=1).add(offer_button)
    offer_keyboard .add(home_button)
    return offer_keyboard


def uncompl_offer_kb(user_id, offer_id):
    connect_button = InlineKeyboardButton(text='📞📞 НАПИСАТЬ КЛИЕНТУ 📞📞', callback_data=f'connect:{user_id}')
    close_button = InlineKeyboardButton(text='❌❌ ЗАКРЫТЬ ЗАЯВКУ ❌❌', callback_data=f'close:{offer_id}')
    uncompl_keyboard = InlineKeyboardMarkup(row_width=1).add(connect_button, close_button, home_button)
    return uncompl_keyboard

def compl_offer_kb(offer_id):
    open_button = InlineKeyboardButton(text='✅✅ ВОЗОБНОВИТЬ ЗАЯВКУ ✅✅', callback_data=f'open:{offer_id}')
    uncompl_keyboard = InlineKeyboardMarkup(row_width=1).add(open_button, home_button)
    return uncompl_keyboard