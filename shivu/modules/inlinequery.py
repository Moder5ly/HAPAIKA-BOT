import re
import time
from cachetools import TTLCache
from pymongo import ASCENDING

from telegram import Update, InlineQueryResultPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import InlineQueryHandler, CallbackContext
from shivu import SUPPORT_ID

from shivu import (
    application,
    database,
    db_user_collections,
    db_character_cards
)

from shivu.modules.messages import (
    msg_info_general_card,
    msg_info_user_card,
    gender_map4,
    rarity_map1,
    gender_map5
)

# collection
database.characters.create_index([('id', ASCENDING)])
database.characters.create_index([('title', ASCENDING)])
database.characters.create_index([('picture_url', ASCENDING)])

# db_user_collections
database.db_user_collections.create_index([('characters.id', ASCENDING)])
database.db_user_collections.create_index([('characters.name', ASCENDING)])
database.db_user_collections.create_index([('characters.picture_url', ASCENDING)])

all_characters_cache = TTLCache(maxsize=10000, ttl=5)
user_collection_cache = TTLCache(maxsize=10000, ttl=5)


async def inline_query(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            if user_id in user_collection_cache:
                user = user_collection_cache[user_id]
            else:
                user = await db_user_collections.find_one({'id': int(user_id)})
                user_collection_cache[user_id] = user

            if user:
                all_characters = list({v['id']: v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [
                        character for character in all_characters
                        if regex.search(character['name']) or regex.search(character['title'])
                    ]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(await db_character_cards.find(
                {"$or": [
                    {"name": regex},
                    {"title": regex}
                ]}
            ).to_list(length=None))
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = list(await db_character_cards.find({}).to_list(length=None))
                all_characters_cache['all_characters'] = all_characters

    characters = all_characters[offset:offset + 50]

    if len(characters) > 50:
        characters = characters[:50]
        next_offset = str(offset + 50)
    else:
        next_offset = str(offset + len(characters))

    results = []
    for character in characters:
        global_count = await db_user_collections.count_documents({'characters.id': character['id']})

        # виведення карток колекції користувача
        if query.startswith('collection.'):
            user_character_count = sum(
                c['id'] == character['id'] for c in user['characters']
            )

            message_card = msg_info_user_card.split('|')
            mention_author = ""

            # уточнення автора картинки, якщо відомий
            if character['picture_author'] != "Невідомий":
                mention_author = "\n\nАвтор картинки: <code>" + character['picture_author'] + "</code>"

            caption = (message_card[0] + gender_map4[character['gender']] +
                       message_card[1] + user.get('first_name', user['id']) +
                       message_card[2] + character['title'] +
                       message_card[3] + str(character['id']) +
                       message_card[4] + character['name'] +
                       message_card[5] + rarity_map1[character['rarity']].split(' ')[0] +
                       message_card[6] + str(user_character_count)) + mention_author

            keyboard = [[]]

        # виведення карток серед усіх
        else:
            message_card = msg_info_general_card.split('|')
            mention_author = ""

            # уточнення автора картинки, якщо відомий
            if character['picture_author'] != "Невідомий":
                mention_author = "Автор картинки: <code>" + character['picture_author'] + "</code>\n"

            caption = (message_card[0] + gender_map4[character['gender']] +
                       message_card[1] + character['title'] +
                       message_card[2] + str(character['id']) +
                       message_card[3] + character['name'] +
                       message_card[4] + rarity_map1[character['rarity']].split(' ')[0] +
                       message_card[5] + mention_author +
                       gender_map5[character['gender']].capitalize() +
                       message_card[6] + str(global_count) +
                       message_card[7])

            keyboard = [
                [InlineKeyboardButton("⚠️ Доповісти про ШІ", url=f'http://t.me/{SUPPORT_ID}')]
            ]

        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['picture_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['picture_url'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

# хендлер інлайну
application.add_handler(
    InlineQueryHandler(inline_query, block=False)
)