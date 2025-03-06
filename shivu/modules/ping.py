import time

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application

async def ping(update: Update, context: CallbackContext) -> None:
    start_time = time.time()
    message = await update.message.reply_text('Понг!')
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 3)
    await message.edit_text(f'Понг! 🏓\n{elapsed_time} мс.')

# хендлер команди /ping, викликає функцію зing()
application.add_handler(CommandHandler("ping", ping))