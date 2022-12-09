from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


cancel_button = KeyboardButton('📛Завершить диалог')

cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add(cancel_button)

