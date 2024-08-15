import random
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from shivu import application, PHOTO_URL, BOT_USERNAME, db
from shivu import pm_users as collection 

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:        
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})   
            else:    
        if user_data['first_name'] != first_name or user_data['username'] != username: 
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    if update.effective_chat.type == "private":   
        caption = f"""***Привіт!***

                        ***Я - бот для відлову різних няшок! ​Додаси мене у свій чат, і я надсилатиму різних няшок кожні 100 (або більше - це можна змінити!) повідомлень, і відгадавши няшку, ти отримаєш її до свого гарему. Не барися - додавай до свого чату і починай збирати власний гарем!***"""
        
        keyboard = [
            [InlineKeyboardButton("ДОДАТИ ДО ЧАТУ", url = f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [InlineKeyboardButton("КОМАНДИ БОТА", callback_data = 'help')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo = photo_url, caption = caption, reply_markup = reply_markup, parse_mode = 'markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [
            [InlineKeyboardButton("ДОДАТИ ДО ЧАТУ", url = f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [InlineKeyboardButton("КОМАНДИ БОТА", callback_data = 'help')],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id = update.effective_chat.id, photo = photo_url, caption = "🎴На місці!?\nБільше інформації про використання - у ПП!", reply_markup = reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """***Команди бота:***
    
                        ***/guess - відгадати няшку (працює лише в чаті)***
                        ***/fav - встановити няшку як улюблену***
                        ***/trade - обмінятися няшками (працює лише в чаті)***
                        ***/collection - глянути свій гарем***
                        ***/ctop - глянути топ чату за к-стю няшок***
                        ***/changetime - змінити періодичність появи няшок (працює лише в чаті)***"""
        help_keyboard = [[InlineKeyboardButton("⤾ Назад", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)
        
        await context.bot.edit_message_caption(chat_id = update.effective_chat.id, message_id = query.message.message_id, caption = help_text, reply_markup = reply_markup, parse_mode = 'markdown')

    elif query.data == 'back':
        caption = f"""***Привіт!***

                        ***Я - бот для відлову різних няшок! ​Додаси мене у свій чат, і я надсилатиму різних няшок кожні 100 (або більше - це можна змінити!) повідомлень, і відгадавши няшку, ти отримаєш її до свого гарему. Не барися - додавай до свого чату і починай збирати власний гарем!***"""
    
        keyboard = [
            [InlineKeyboardButton("ДОДАТИ ДО ЧАТУ", url = f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [InlineKeyboardButton("КОМАНДИ БОТА", callback_data = 'help')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(chat_id = update.effective_chat.id, message_id = query.message.message_id, caption = caption, reply_markup = reply_markup, parse_mode = 'markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)
