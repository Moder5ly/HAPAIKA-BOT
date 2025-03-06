from pymongo import ReturnDocument
from pyrogram.enums import ChatMemberStatus

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, bot, db_message_frequencies
from shivu.modules.messages import (
    msg_error_not_chat_admin,
    msg_error_too_many_args,
    msg_error_frequency,
    msg_error_generic,
    msg_success_changed_freq
)


async def change_frequency(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    member = await bot.get_chat_member(
        chat_id,
        user_id
    )

    admins = [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]

    # якщо користувач не адмін чату, то блокує використання
    if member.status not in admins:
        message_error1 = msg_error_not_chat_admin.split('|')

        await update.message.reply_text(
            message_error1[0] + update.effective_user.first_name + message_error1[1]
        )
        return

    try:
        args = context.args

        # якщо більше одного аргумента, то фейл команди
        if len(args) != 1:
            message_error2 = msg_error_too_many_args.split('|')

            await update.message.reply_text(
                message_error2[0] + update.effective_user.first_name + message_error2[1],
                parse_mode='HTML'
            )
            return

        # ЗМЕНШИТИ З ЧАСОМ
        min_frequency = 500
        new_frequency = int(args[0])

        # якщо частота занизька, то фейл команди
        if new_frequency < min_frequency:
            message_error3 = msg_error_frequency.split('|')

            await update.message.reply_text(
                message_error3[0] + update.effective_user.first_name + message_error3[1] + str(min_frequency) + '.'
            )
            return

        chat_frequency = await db_message_frequencies.find_one_and_update(
            {'chat_id': str(chat_id)},
            {'$set': {'frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        message_success = msg_success_changed_freq.split('|')

        await update.message.reply_text(
            message_success[0] + message_success[1] + str(new_frequency) + '.'
        )

    except Exception as e:
        message_error4 = msg_error_generic.split('|')

        await update.message.reply_text(
            message_error4[0] + update.effective_user.first_name + message_error4[1] + str(e) + '.'
        )


# хендлер команди /frequency, викликає функцію change_frequency()
application.add_handler(
    CommandHandler(["frequency", "freq", "changetime"], change_frequency, block=False)
)
