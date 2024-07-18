import importlib
import time
import random
import re
import asyncio
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, db, LOGGER
from shivu.modules import ALL_MODULES

from datetime import datetime

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

last_user = {}
warned_users = {}
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:        
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 100)
        else:
            message_frequency = 100
        
        #антиспам функція
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 1000:
            
                if user_id in warned_users and time.time() - warned_users[user_id] < 300:
                    return
                else:                    
                    await update.message.reply_text(f"{update.effective_user.first_name}, не спамити!\nТепер близько 5 хвилин твої повідомлення будуть проігноровані.")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}
  
        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

        #поява няші, якщо к-сть повідомлення = заданій частоті повідомлень
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            
            message_counts[chat_id] = 0

        #ріп няші, якщо досягнуто половини повідомлень від частоти повідомлень
        if message_counts[chat_id] == 5:
            await kill_waifu(update, context)
            
# функція появи няшки            
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    all_characters = list(await collection.find({}).to_list(length = None))
    
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    #тут вибирається няша з усієї бази
    current_month = datetime.now().month
#    event_map =  {
#                     1: "🐾 Твариноподібна", 
#                     2: "👘 Східна", 
#                     3: "🎉 Знаменна", 
#                     4: "🐰 Великодня",
#                     5: "👯‍♂️ Парна",
#                     6: "🌈 Статезмінна",
#                     7: "🏖️ Пляжна",
#                     8: "🧹 Покоївкова",
#                     9: "👩‍🏫 Шкільна",
#                     10: "🎃 Геловінська",
#                     11: "🍔 Гамбургерна",
#                     12: "🎄 Різдвяна",
#                     13: "⚪️ Звичайна"
#                     }
    
    character = random.choice([c for c in all_characters if c['event'] == current_month or c['event'] == "0"])

    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    #виведення няші
    await context.bot.send_photo(
        chat_id = chat_id,
        photo = character['img_url'],
        caption = f"З'явилася няшка!\n\n<code>/guess</code> <i>ім'я/прізвище няшки</i>, аби додати до свого гарему.",
        parse_mode = 'HTML')

# функція смерті
async def kill_waifu(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    if chat_id not in last_characters:
        return

    first_correct_guesses[chat_id] = -1
    sent_characters[chat_id] = []

    #виведення повідомлення
    await context.bot.send_message(
        chat_id = chat_id, 
        text = f"❌️ Ой біда, няшка втекла, бо ніхто не встиг відгадати!\n\nЦе була <code><b>{last_characters[chat_id]['name']}</b></code>\nТайтл: <code><b>{last_characters[chat_id]['anime']}</b></code>.", 
         parse_mode = 'HTML')

# функція відгадування
async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f"❌️ Няшку більше не можна залутати. Успіхів наступного разу!")
        return

    guess = ' '.join(context.args).lower() if context.args else ''
    
    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text(f"❌️ Такі символи не можна вживати.")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()
    translit_name_parts = last_characters[chat_id]['name_translit'].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts) or sorted(translit_name_parts) == sorted(guess.split()) or any(tpart == guess for tpart in translit_name_parts):
    
        first_correct_guesses[chat_id] = user_id
        
        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})
            
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
      
        elif hasattr(update.effective_user, 'username'):
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
            })

        group_user_total = await group_user_totals_collection.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$set': update_fields})
            
            await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$inc': {'count': 1}})
      
        else:
            await group_user_totals_collection.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })

        group_info = await top_global_groups_collection.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await top_global_groups_collection.update_one({'group_id': chat_id}, {'$set': update_fields})
            
            await top_global_groups_collection.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})
      
        else:
            await top_global_groups_collection.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })
       
        keyboard = [[InlineKeyboardButton(f"Переглянути гарем", switch_inline_query_current_chat = f"collection.{user_id}")]]

        await update.message.reply_text(f"<b><a href='tg://user?id={user_id}'>{escape(update.effective_user.first_name)}</a></b> відгадав/відгадала няшку!\n\nЦе <b>{last_characters[chat_id]['name']}</b>!\nТайтл: <code><b>{last_characters[chat_id]['anime']}</b></code>.", parse_mode = 'HTML', reply_markup = InlineKeyboardMarkup(keyboard))

    else:
        await update.message.reply_text("❌️ Неправильне ім'я/прізвище!")
   
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
   
    if not context.args:
        await update.message.reply_text('Надай ідентифікатор няшки.')
        return

    character_id = context.args[0]
    
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('У твоєму гаремі зовсім немає няшок.')
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('Ця няшка не у твоєму гаремі.')
        return
    
    user['favorites'] = [character_id]
    
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})
    await update.message.reply_text(f'✅ Няшку {character["name"]} встановлено, як улюблену.')
    
def main() -> None:
    """Бота запущено."""

    application.add_handler(CommandHandler(["guess", "protecc", "collect", "grab", "hunt"], guess, block = False))
    application.add_handler(CommandHandler("fav", fav, block = False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block = False))

    application.run_polling(drop_pending_updates = True)
    
if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Бота запущено.")
    main()
