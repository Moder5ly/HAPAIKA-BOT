import math, random
from itertools import groupby
from html import escape

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler

from shivu import application, db_character_cards, db_user_collections

from shivu.modules.messages import (
    msg_info_no_cards
)


async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id

    user = await db_user_collections.find_one({'id': user_id})
    if not user:
        message_info = msg_info_no_cards.split('|')

        if update.message:
            await update.message.reply_text(
                message_info[0] + update.effective_user.first_name + message_info[1]
            )
        else:
            await update.callback_query.edit_message_text(
                message_info[0] + update.effective_user.first_name + message_info[1]
            )
        return

    characters = sorted(user['characters'], key=lambda x: (x['title'], x['id']))

    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    unique_characters = list({character['id']: character for character in characters}.values())

    total_pages = math.ceil(len(unique_characters) / 15)  

    if page < 0 or page >= total_pages:
        page = 0  

    collection_message = (f"<b>Колекція {escape(update.effective_user.first_name)} - "
                          f"Сторінка {page+1}/{total_pages}</b>\n")

    current_characters = unique_characters[page*15:(page+1)*15]

    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['title'])}

    for anime, characters in current_grouped_characters.items():
        collection_message += (f'\n<b>{anime} - {len(characters)}/'
                               f'{await db_character_cards.count_documents({"title": anime})}</b>\n')

        for character in characters:
            count = character_counts[character['id']]  
            collection_message += f'{character["id"]}. {character["name"]} x{count}\n'

    total_count = len(user['characters'])
    
    keyboard = [[InlineKeyboardButton(f"Колекція з {total_count} карток",
                                      switch_inline_query_current_chat=f"collection.{user_id}")]]

    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"harem:{page-1}:{user_id}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"harem:{page+1}:{user_id}"))
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if 'favorites' in user and user['favorites']:
        fav_character_id = int(user['favorites'][0])
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)

        if fav_character and 'picture_url' in fav_character:
            if update.message:
                await update.message.reply_photo(
                    photo=fav_character['picture_url'],
                    parse_mode='HTML',
                    caption=collection_message,
                    reply_markup=reply_markup
                )
            else:
                
                if update.callback_query.message.caption != collection_message:
                    await update.callback_query.edit_message_caption(
                        caption=collection_message,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
        else:
            if update.message:
                await update.message.reply_text(
                    collection_message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            else:
                
                if update.callback_query.message.text != collection_message:
                    await update.callback_query.edit_message_text(
                        collection_message,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
    else:
        if user['characters']:
        
            random_character = random.choice(user['characters'])

            if 'picture_url' in random_character:
                if update.message:
                    await update.message.reply_photo(
                        photo=random_character['picture_url'],
                        parse_mode='HTML',
                        caption=collection_message,
                        reply_markup=reply_markup
                    )
                else:
                    
                    if update.callback_query.message.caption != collection_message:
                        await update.callback_query.edit_message_caption(
                            caption=collection_message,
                            reply_markup=reply_markup,
                            parse_mode='HTML'
                        )
            else:
                if update.message:
                    await update.message.reply_text(
                        collection_message,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                else:
                
                    if update.callback_query.message.text != collection_message:
                        await update.callback_query.edit_message_text(
                            collection_message,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
        else:
            if update.message:
                await update.message.reply_text("Твоя колекція пуста.")


# не зовсім ясно, що це за функція, але най буде
async def harem_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    _, page, user_id = data.split(':')

    page = int(page)
    user_id = int(user_id)

    if query.from_user.id != user_id:
        await query.answer("❌️ Це не твоя колекція!", show_alert=True)
        return

    await harem(update, context, page)


# хендлер команд
application.add_handler(
    CommandHandler(["harem", "collection"], harem,block=False)
)

harem_handler = CallbackQueryHandler(harem_callback, pattern='^harem', block=False)
application.add_handler(harem_handler)