from telegram import Update
from telegram.ext import CallbackContext, CommandHandler 

from shivu import application, db_users, db_top_global_groups, OWNER_ID

from shivu.modules.messages import (
    msg_error_non_auth_user,
    msg_alert_not_reply,
    msg_info_broadcast
)


async def broadcast(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != int(OWNER_ID):
        message_error = msg_error_non_auth_user.split('|')

        await update.message.reply_text(
            message_error[0] + update.effective_user.first_name + message_error[1]
        )
        return

    # повідомлення має бути форвардом, тому треба
    # відписати на повідомлення, щоб відправити
    message_to_broadcast = update.message.reply_to_message

    # якщо не відписано, то фейл команди
    if message_to_broadcast is None:
        message_error = msg_alert_not_reply.split('|')

        await update.message.reply_text(
            message_error[0] + update.effective_user.first_name + message_error[1]
        )
        return

    all_chats = await db_top_global_groups.distinct("group_id")
    all_users = await db_users.distinct("_id")

    channel_list = list(set(all_chats + all_users))

    failed_sends = 0

    for chat_id in channel_list:
        try:
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=message_to_broadcast.chat_id,
                message_id=message_to_broadcast.message_id
            )
        except Exception as e:
            print(f"Не вдалося відправити повідомлення до {chat_id}. Помилка: {e}")
            failed_sends += 1

    message_info = msg_info_broadcast.split('|')

    await update.message.reply_text(
        message_info[0] + message_info[1] + str(failed_sends) + message_info[2]
    )

application.add_handler(CommandHandler("broadcast", broadcast, block=False))
