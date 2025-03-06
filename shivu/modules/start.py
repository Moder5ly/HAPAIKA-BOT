import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from shivu import application, PHOTO_URL, UPDATE_CHANNEL, BOT_USERNAME
from shivu import db_users

from shivu.modules.messages import (
    msg_bot_started_in_pm,
    msg_bot_started_in_chat,
    msg_bot_help_section
)


# функція команди start
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await db_users.find_one({"_id": user_id})

    # якщо юзер вперше користується
    # командою, то додаємо його в базу
    if user_data is None:
        # додавання в БД
        await db_users.insert_one(
            {"_id": user_id, "first_name": first_name, "username": username}
        )

    # якщо користується не вперше
    else:
        # то перевіряємо чи збігається ЮН та ім'я,
        # якщо щось із цього ні - оновлюємо
        if user_data['first_name'] != first_name or user_data['username'] != username:
            await db_users.update_one(
                {"_id": user_id},
                {"$set":
                     {"first_name": first_name, "username": username}
                }
            )

    # якщо команда була використана
    # в приватній переписці бота
    if update.effective_chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("ДОДАТИ МЕНЕ ДО ЧАТУ", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [InlineKeyboardButton("Оновлення", url=f'https://t.me/{UPDATE_CHANNEL}'),
             InlineKeyboardButton("Посібник", callback_data='help')],
        ]

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=random.choice(PHOTO_URL),
            caption=msg_bot_started_in_pm,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    # якщо команда була використана у чаті
    else:
        keyboard = [
            [InlineKeyboardButton("Оновлення", url=f'https://t.me/{UPDATE_CHANNEL}'),
             InlineKeyboardButton("Посібник", callback_data='help')],
        ]

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=random.choice(PHOTO_URL),
            caption=msg_bot_started_in_chat,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await context.bot.edit_message_caption(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            caption=msg_bot_help_section,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⤾ Повернутися", callback_data='back')]]),
            parse_mode='HTML'
        )

    elif query.data == 'back':
        if update.effective_chat.type == "private":
            keyboard = [
                [InlineKeyboardButton("ДОДАТИ МЕНЕ ДО ЧАТУ", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
                [InlineKeyboardButton("Оновлення", url=f'https://t.me/{UPDATE_CHANNEL}'),
                 InlineKeyboardButton("Посібник", callback_data='help')],
            ]

            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=query.message.message_id,
                caption=msg_bot_started_in_pm,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

        # якщо команда була використана у чаті
        else:
            keyboard = [
                [InlineKeyboardButton("Оновлення", url=f'https://t.me/{UPDATE_CHANNEL}'),
                 InlineKeyboardButton("Посібник", callback_data='help')],
            ]

            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=query.message.message_id,
                caption=msg_bot_started_in_chat,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

# хендлер кнопок для зміни повідомлення
application.add_handler(
    CallbackQueryHandler(button, pattern='^help$|^back$', block=False)
)

# хендлер команд для функції start
application.add_handler(
    CommandHandler(["start", "info", "help" "information"], start, block=False)
)