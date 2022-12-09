from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode


async def get_chat_id(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    print(user_id, chat_id)


async def bot_echo(message: types.Message):
    text = [
        "Эхо без состояния.",
        "Сообщение:"
    ]
    await message.answer('\n'.join(text))

    await message.answer('\n'.join(text))


async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f'Эхо в состоянии {hcode(state_name)}',
        'Содержание сообщения:',
        hcode(message.text)
    ]
    await message.answer('\n'.join(text))


def register_echo(dp: Dispatcher):
    dp.register_message_handler(get_chat_id, state='*', commands='get_id')
    # dp.register_message_handler(bot_echo)
    # dp.register_message_handler(bot_echo_all, state="*", content_types=types.ContentTypes.ANY)
