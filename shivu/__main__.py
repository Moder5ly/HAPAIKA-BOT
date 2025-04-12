import importlib, time, random, asyncio, re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu.modules import ALL_MODULES

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

from shivu import (
    bot,
    db_character_cards,
    db_top_global_groups,
    db_group_user_totals,
    db_user_collections,
    db_message_frequencies
)
from shivu import application, LOGGER

from shivu.modules.messages import (
    msg_alert_dont_spam,
    msg_info_card_lost,
    msg_info_card_appear,
    msg_error_card_guessed,
    msg_encouragement,
    msg_button_label_inline,
    msg_success_guessed,
    msg_error_wrong_name,
    msg_error_wrong_cmd,
    msg_error_no_cards,
    msg_error_not_in_coll,
    msg_success_set_fav
)

from shivu.modules.messages import (
    gender_map1,
    gender_map2,
    gender_map3,
    rarity_map1,
)

# збирає інформацію про останню картку,
# яку видавали в кожному чаті
last_card = {}

# збирає інформацію про всі унікальні
# картки, які видавали в кожному чаті
sent_cards = {}

# збирає інформацію про юзера, який
# відгадав картку у чаті, щоби казати
# потім іншим юзерач у чаті, шо вони
# лохи жоскі
guesses = {}

# якісь словники, які хуй його пойми для чого
locks = {}
message_counts = {}

# словники, що стосуються антиспам-функціоналу
warned_users = {}
last_user = {}


# функція підрахування повідомлень
async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        # шукаємо кастомну частоту повідомлень
        # якщо є, то встановлюється кастомна
        # якщо нема, то ставиться дефолтна
        chat_frequency = await db_message_frequencies.find_one(
            {'chat_id': chat_id}
        )
        if chat_frequency:
            message_frequency = chat_frequency.get('frequency', 10)
        else:
            message_frequency = 250

        # антиспам функція
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 100000:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    message_alert = msg_alert_dont_spam.split('|')
                    await update.message.reply_text(
                        message_alert[0] + update.effective_user.first_name + message_alert[1]
                    )
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # шукаємо айдішку чату у масиві message_counts, якщо
        # знаходимо, то додаємо +1 до підрахунку повідомлень,
        # інакше додаємо чат ід до масиву зі значенням 1
        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

        # поява картки, якщо к-сть повідомлень = заданій частоті повідомлень у чаті
        if message_counts[chat_id] % message_frequency == 0:
            await send_card(update, context)

        # чистка картки, якщо досягнуто 1.5x повідомлень від частоти
        if message_counts[chat_id] / message_frequency >= 1.5:
            message_info = msg_info_card_lost.split('|')

            # виведення повідомлення про втрату картку, якщо ніхто не вгадав
            if int(chat_id) not in guesses:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message_info[0] + gender_map3[last_card[int(chat_id)]['gender']] +
                         message_info[1] + gender_map1[last_card[int(chat_id)]['gender']] +
                         message_info[2] + last_card[int(chat_id)]['name'] +
                         message_info[3] + last_card[int(chat_id)]['title'] +
                         message_info[4],
                    parse_mode='HTML'
                )

            del last_card[int(chat_id)]
            message_counts[chat_id] = 0


# функція надсилання картки
async def send_card(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # збираємо всі картки з БД
    character_cards = list(
        await db_character_cards.find({}).to_list(length=None)
    )

    # якщо не знаходимо чат у словнику, то додаємо його туди
    if chat_id not in sent_cards:
        sent_cards[chat_id] = []

    # чистимо список відправлених унікальних
    # карток у чаті, якщо досягає к-сті всіх
    # можливих карток
    if len(sent_cards[chat_id]) == len(character_cards):
        sent_cards[chat_id] = []

    '''ТУТ МАЄ БУТИ КОД ДЛЯ ВИЗНАЧЕННЯ ІВЕНТІВ'''

    # вибираємо випадкову картку з тих,
    # що ще не відправлені
    card = random.choice(
        [c for c in character_cards if c['rarity'] == 0 and c['id'] not in sent_cards[chat_id]]
    )

    LOGGER.info(card)
    # додаємо вибрану картку до списку надісланих
    sent_cards[chat_id].append(card['id'])
    last_card[chat_id] = card

    # якщо знаходимо чат у відгаданих, то чистим,
    # щоби не писало, що вже хтось залутав
    if chat_id in guesses:
        del guesses[chat_id]

    message_info = msg_info_card_appear.split('|')
    # власне, надсилання картки
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=card['picture_url'],
        caption=message_info[0] + rarity_map1[last_card[int(chat_id)]['rarity']].split(' ')[1] +
                message_info[1] + gender_map3[last_card[int(chat_id)]['gender']] +
                message_info[2] + gender_map2[last_card[int(chat_id)]['gender']] +
                message_info[3],
        parse_mode='HTML'
    )


async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # об'єднання аргументів (слів) у один рядок,
    # розділений пробілами
    guess_word = ' '.join(context.args).lower() if context.args else ''

    # якщо останньої картки нема у чаті
    # (втрачена або відгадана), то нічого
    # не відповідати на використання команди
    if chat_id not in last_card:
        return

    # якщо вже відгадано, але хтось намагається
    # ще раз, то відмовляємо
    if chat_id in guesses:
        message_error = msg_error_card_guessed.split('|')

        await update.message.reply_text(
            message_error[0] + update.effective_user.first_name +
            message_error[1] + msg_encouragement[random.randint(0, 5)]
        )
        return

    # якщо хтось вводить неправильні символи
    if "()" in guess_word or "&" in guess_word.lower():
        return

    # ділимо імена в картці
    name_parts = re.split(' |, ', last_card[chat_id]['name'].lower())

    # якщо ім'я/прізвище правильне
    if sorted(name_parts) == sorted(guess_word.split()) or any(part == guess_word for part in name_parts):
        # записуємо ід юзера з чату, який вгадав
        guesses[chat_id] = user_id
        # за user_id знаходимо юзера в БД
        user = await db_user_collections.find_one({'id': user_id})

        # якщо юзера знайшли
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await db_user_collections.update_one({'id': user_id}, {'$set': update_fields})

            await db_user_collections.update_one({'id': user_id}, {'$push': {'characters': last_card[chat_id]}})

        elif hasattr(update.effective_user, 'username'):
            await db_user_collections.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [
                    last_card[chat_id]
                ],
            })

        group_user_total = await db_group_user_totals.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get(
                    'username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await db_group_user_totals.update_one(
                    {'user_id': user_id,
                     'group_id': chat_id},
                    {'$set': update_fields}
                )

            await db_group_user_totals.update_one(
                {'user_id': user_id,
                 'group_id': chat_id},
                {'$inc':
                     {'count': 1}
                 })

        else:
            await db_group_user_totals.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })

        group_info = await db_top_global_groups.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await db_top_global_groups.update_one({'group_id': chat_id}, {'$set': update_fields})

            await db_top_global_groups.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})

        else:
            await db_top_global_groups.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })

        keyboard = [
            [InlineKeyboardButton(msg_button_label_inline,
                                  switch_inline_query_current_chat=f"collection.{user_id}")]
        ]
        message_success = msg_success_guessed.split('|')

        await update.message.reply_text(
            gender_map3[last_card[chat_id]['gender']].capitalize() +
            message_success[0] + gender_map1[last_card[chat_id]['gender']] +
            message_success[1] + last_card[chat_id]['name'] +
            message_success[2] + last_card[chat_id]['title'] +
            message_success[3] + update.effective_user.first_name +
            message_success[4],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # якщо ім'я/прізвище неправильне
    else:
        message_error = msg_error_wrong_name.split('|')

        await update.message.reply_text(
            message_error[0] + update.effective_user.first_name + message_error[1]
        )


# функція вибирання улюбленої картинки
async def favourite(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # якщо команда введена неправильно, то фейл
    if not context.args or len(context.args) > 1:
        message_error1 = msg_error_wrong_cmd.split('|')

        await update.message.reply_text(
            message_error1[0] + update.effective_user.first_name + message_error1[1],
            parse_mode='HTML'
        )
        return

    # якщо користувача нема в БД (нема карток), то фейл команди
    user = await db_user_collections.find_one({'id': user_id})

    if not user:
        message_error2 = msg_error_no_cards.split('|')

        await update.message.reply_text(
            message_error2[0] + update.effective_user.first_name + message_error2[1]
        )
        return

    # якщо картки немає, то фейл команди
    character_id = context.args[0]
    character = next((c for c in user['characters'] if int(c['id']) == int(character_id)), None)

    if not character:
        message_error3 = msg_error_not_in_coll.split('|')

        await update.message.reply_text(
            message_error3[0] + update.effective_user.first_name + message_error3[1]
        )
        return

    user['favorites'] = [character_id]

    # оновлення улюбленої картки у БД
    await db_user_collections.update_one(
        {'id': user_id},
        {'$set':
             {'favorites': user['favorites']}
         }
    )

    # ділимо повідомлення для виводу
    message_success = msg_success_set_fav.split('|')

    await update.message.reply_text(
        message_success[0] + update.effective_user.first_name + message_success[1] + character["name"] +
        message_success[2]
    )


def main() -> None:
    # команди на лут, які активовують функцію guess()
    application.add_handler(
        CommandHandler(["guess", "protecc", "collect", "grab", "hunt", "catch", "protect"], guess, block=False)
    )

    # команди, які активовують функцію fav() - МОЖЕ перенести в окремий модуль?
    application.add_handler(
        CommandHandler(["favorite", "fav"], favourite, block=False)
    )

    # хендлер для повідомлень, який підраховує смски, функція message_counter()
    application.add_handler(
        MessageHandler(filters.ALL, message_counter, block=False)
    )

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    # запуск бота
    bot.start()
    LOGGER.info("Бот запущений.")

    # запуск головної функції
    main()
