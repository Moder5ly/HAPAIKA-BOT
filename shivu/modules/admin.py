import logging
import urllib.request
from pymongo import ReturnDocument

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from shivu import application, sudo_users, collection, db

# Увімкнення логування
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                    level=logging.INFO)

#logger = logging.getLogger(__name__)

# Cтани для додавання
SET_IMAGE, SET_NAME, SET_TITLE, SET_EVENT, SET_TAGS, ADD_TO_DATABASE = range(6)

# Стани для оновлення
SET_FIELD, SET_NEWVALUE, UPDATE_TEXT, UPDATE_TITLE, UPDATE_EVENT, UPDATE_IMAGE = range(6)

# Рядки для виведення
message_notice_cannot_use           = "⚠️ Тобі не можна користуватися цією командою."
message_notice_cancel_command       = ("⚠️ На будь-якому кроці користуйся командою /cancel, "
                                       "якщо хочеш скасувати всю дію.")
message_notice_double_check         = "⚠️ Перевір, чи все введено правильно, і завершуй."
message_notice_action_cancelled     = "⚠️ Дію скасовано."

message_error_incorrect_image_url   = ("❌️ Некоректне посилання. Спробуй завантажити картинку "
                                       "на якийсь хостинг та вставляй пряме посилання звідти.")
message_error_could_not_add_image   = ("❌️ Не вдалося додати картинку. Напиши Модеру і дай йому "
                                       "текст помилки, а там буде видно.")
message_error_could_not_find_image  = "❌️ Картинку з таким кодом не знайдено: "
message_error_field_doesnt_exist    = "❌️ Такого поля не існує. Обирай з кнопок!"

message_success_image_added         = "✅ Картинку успішно додано до бази даних! Тепер вона може випадати!"
message_success_image_updated       = "✅ Значення успішно оновлено!"

message_at_upload_start             = "Ти додаєш картинку."
message_at_update_start             = "Ти редагуєш дані картинки."
message_at_removal_start            = "Ти видаляєш картинку."
message_showing_chara_name          = "Вказане ім'я персонажа/ів: "
message_showing_title_name          = "Обрана назва тайтлу: "
message_showing_event_selected      = "Обраний варіант картинки: "
message_showing_ID_found            = "Знайдено персонажа за кодом "
message_showing_current_value       = "Поточн"

message_request_enter_image_url     = "Введи пряме посилання на картинку."
message_request_enter_chara_name    = "Введи ім'я персонажа/ів українською мовою."
message_request_enter_title_name    = ("Введи назву тайтлу українською мовою. Назву тайтлу можна "
                                       "ввести як вручну, так і обравши з доступних кнопок.")
message_request_select_event        = "Обери варіант картинки."
message_request_enter_tags          = ("Введи додаткові теґи <b>через пробіл</b>. Теґами можуть бути: "
                                       "транслітерація імені персонажа англійською, прізвиська тощо.")
message_request_enter_chara_ID      = "Введи код картинки."
message_request_select_field        = "Обери, що саме бажаєш виправити."
message_request_enter_new_value     = "Введи нов"

title_name1                         = "Милий у Франксі"
title_name2                         = "Мій братик вже не братик!"
title_name3                         = "Магічна битва"

event_name_common                   = "⚪️ Звичайний"
event_name_christmas                = "🎄 Різдвяний"
event_name_summer                   = "🏖️ Літній"
event_name_halloween                = "🎃 Геловінський"

button_ok                           = "✅ Усе правильно"
button_edit                         = "⚠️ Відредагувати"

field_name1                         = "Ім'я"
field_name2                         = "Тайтл"
field_name3                         = "Теґи"
field_name4                         = "Варіант"
field_name5                         = "Картинка"


###
#
# ДОДАВАННЯ
#
###

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Початок додавання, введення посилання."""
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text(message_notice_cannot_use)
        return
    else:
        await update.message.reply_text("<b>" + message_at_upload_start + "</b>\n" + message_notice_cancel_command,
                                        parse_mode='HTML')

        await update.message.reply_text(message_request_enter_image_url,
                                        parse_mode='HTML')

        return SET_IMAGE


async def set_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запис посилання у змінну, перевірка посилання, вказування імені персонажа/персонажів."""
    context.user_data['image_url'] = update.message.text

    try:
        urllib.request.urlopen(context.user_data['image_url'])
    except:
        await update.message.reply_text(message_error_incorrect_image_url)
        return await upload_start(update, context)

    await update.message.reply_text(message_request_enter_chara_name,
                                    parse_mode='HTML')
    return SET_NAME


async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запис імені у змінну, вибір тайтлу."""
    context.user_data['chara_name'] = update.message.text
    entered_character_name = context.user_data['chara_name']

    keyboard_markup = [
        [InlineKeyboardButton(title_name1, callback_data=title_name1)],
        [InlineKeyboardButton(title_name2, callback_data=title_name2)],
        [InlineKeyboardButton(title_name3, callback_data=title_name3)]
    ]
    keyboard = InlineKeyboardMarkup(keyboard_markup)

    await update.message.reply_text("<b>" + message_showing_chara_name + entered_character_name +
                                    "</b>\n\n" + message_request_enter_title_name,
                                    parse_mode='HTML',
                                    reply_markup=keyboard)
    return SET_TITLE


async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запис тайтлу у змінну, вибір варіанту."""
    query = update.callback_query
    await query.answer()
    context.user_data['title_name'] = query.data

    keyboard_markup = [
        [InlineKeyboardButton(event_name_common, callback_data=event_name_common)],
        [InlineKeyboardButton(event_name_christmas, callback_data=event_name_christmas)],
        [InlineKeyboardButton(event_name_summer, callback_data=event_name_summer)],
        [InlineKeyboardButton(event_name_halloween, callback_data=event_name_halloween)]
    ]
    keyboard = InlineKeyboardMarkup(keyboard_markup)

    await query.message.reply_text("<b>" + message_showing_title_name + context.user_data['title_name'] +
                                   "</b>\n\n" + message_request_select_event,
                                   parse_mode='HTML',
                                   reply_markup=keyboard)
    return SET_EVENT


async def set_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запис варіанту у змінну, введення теґів."""
    query = update.callback_query
    await query.answer()
    selected_event = query.data
    context.user_data['event'] = selected_event.split(" ")[0]

    await query.message.reply_text("<b>" + message_showing_event_selected + selected_event +
                                   "</b>\n" + message_request_enter_tags,
                                   parse_mode='HTML')
    return SET_TAGS


async def get_next_sequence_number(sequence_name):
    """Функція бота для отримання ID."""
    sequence_collection = db.sequences

    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'sequence_value': 1}},
        return_document=ReturnDocument.AFTER
    )

    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0

    return sequence_document['sequence_value']


async def set_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запис теґів у змінну, звірення введених даних, перехід до додавання."""
    context.user_data['tags'] = update.message.text
    #image_file = get_file(context.user_data['image_url'])

    selections = context.user_data

    message_summary = (message_notice_double_check + "\n\n" +
                       "<b>" + field_name1 + ":</b> " + selections.get('chara_name') + " " + selections.get('event') +
                       "\n<b>" + field_name2 + ":</b> " + selections.get('title_name') + "\n" +
                       "<b>" + field_name3 + ":</b> <i>" + selections.get('tags') + "</i>")

    keyboard_markup = [
        [InlineKeyboardButton(button_ok, callback_data='сomplete')]
    ]
    keyboard = InlineKeyboardMarkup(keyboard_markup)

    try:
        await context.bot.send_photo(update.effective_chat.id,
                                     photo=context.user_data['image_url'],
                                     reply_markup=keyboard,
                                     caption=message_summary,
                                     parse_mode='HTML')
    except:
        await update.message.reply_text(message_summary,
                                        parse_mode='HTML',
                                        reply_markup=keyboard)
    return ADD_TO_DATABASE


async def add_to_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Залежно від вибору, додавання до бази даних або виправлення."""
    query = update.callback_query
    await query.answer()
    decision = query.data

    identifier = str(await get_next_sequence_number('character_id')).zfill(2)

    character = {
        'img_url': context.user_data['image_url'],
        'name': context.user_data['chara_name'],
        'title': context.user_data['title_name'],
        'event': context.user_data['event'],
        'tags': context.user_data['tags'],
    #   'rarity': rarity,
        'id': identifier,
        'message_id': 0
    }

    try:
        await collection.insert_one(character)
        await query.message.reply_text(message_success_image_added,
                                       reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await update.message.reply_text(message_error_could_not_add_image + "\n\n Помилка: " + str(e),
                                        parse_mode='HTML')

    return ConversationHandler.END


###
#
# ВИПРАВЛЕННЯ
#
###

async def update_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Початок додавання, введення посилання."""
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text(message_notice_cannot_use)
        return
    else:
        await update.message.reply_text("<b>" + message_at_update_start + "</b>\n" + message_notice_cancel_command,
                                        parse_mode='HTML')

        await update.message.reply_text(message_request_enter_chara_ID,
                                        parse_mode='HTML')

        return SET_FIELD


async def set_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запис ідентифікатора у змінну, перевірка ідентифікатора, вибір поля для зміни."""
    context.user_data['chat_id'] = update.effective_chat.id
    character = await collection.find_one({'id': update.message.text})

    if not character:
        await update.message.reply_text(message_error_could_not_find_image + update.message.text)
        return await update_start(update, context)
    else:
        keyboard_markup = [
            [
                InlineKeyboardButton(field_name1, callback_data="name"),
                InlineKeyboardButton(field_name2, callback_data="title"),
                InlineKeyboardButton(field_name3, callback_data="tags")
            ],
            [
                InlineKeyboardButton(field_name4, callback_data="event"),
                InlineKeyboardButton(field_name5, callback_data="img_url")
            ]
        ]
        keyboard = InlineKeyboardMarkup(keyboard_markup)

        context.user_data['character'] = character

        await context.bot.send_photo(chat_id=context.user_data['chat_id'],
                                     caption="<b>" + message_showing_ID_found + update.message.text +
                                             "!</b>\n\n" + character['name'] + " " + character['event'] +
                                             "\n" + character['title'] + "\n<b>Теґи:</b> " + character['tags'] +
                                             "\n\n" + message_request_select_field,
                                     photo=character['img_url'],
                                     reply_markup=keyboard,
                                     parse_mode='HTML')

    return SET_NEWVALUE


async def set_newvalue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Залежно від обраного поля, виводити певний результат і запитувати відповідне нове значення."""
    query = update.callback_query
    await query.answer()
    selected_field = query.data

    context.user_data['selected_field'] = selected_field

    if selected_field == "name":
        await query.message.reply_text("<b>" + message_showing_current_value + "е " + field_name1.lower() +
                                        ": " + context.user_data['character'][selected_field] + "</b>\n\n" +
                                        message_request_enter_new_value + "е " + field_name1.lower() + ".",
                                        parse_mode='HTML')
        return UPDATE_TEXT

    elif selected_field == "title":
        keyboard_markup = [
            [InlineKeyboardButton(title_name1, callback_data=title_name1)],
            [InlineKeyboardButton(title_name2, callback_data=title_name2)],
            [InlineKeyboardButton(title_name3, callback_data=title_name3)]
        ]
        keyboard = InlineKeyboardMarkup(keyboard_markup)

        await query.message.reply_text("<b>" + message_showing_current_value + "ий " + field_name2.lower() +
                                        ": " + context.user_data['character'][selected_field] + "</b>\n\n" +
                                        message_request_enter_new_value + "ий " + field_name2.lower() + ".",
                                        parse_mode='HTML',
                                        reply_markup=keyboard)
        return UPDATE_TITLE

    elif selected_field == "tags":
        await query.message.reply_text("<b>" + message_showing_current_value + "і " + field_name3.lower() +
                                        ": " + context.user_data['character'][selected_field] + "</b>\n\n" +
                                        message_request_enter_new_value + "і " + field_name3.lower() + ".",
                                        parse_mode='HTML')
        return UPDATE_TEXT

    elif selected_field == "event":
        keyboard_markup = [
            [InlineKeyboardButton(event_name_common, callback_data=event_name_common)],
            [InlineKeyboardButton(event_name_christmas, callback_data=event_name_christmas)],
            [InlineKeyboardButton(event_name_summer, callback_data=event_name_summer)],
            [InlineKeyboardButton(event_name_halloween, callback_data=event_name_halloween)]
        ]
        keyboard = InlineKeyboardMarkup(keyboard_markup)

        await query.message.reply_text("<b>" + message_showing_current_value + "ий " + field_name4.lower() +
                                        ": " + context.user_data['character'][selected_field] + "</b>\n\n" +
                                        message_request_enter_new_value + "ий " + field_name4.lower() + ".",
                                        parse_mode='HTML',
                                        reply_markup=keyboard)
        return UPDATE_EVENT

    elif selected_field == "img_url":
        await query.message.reply_text(message_request_enter_new_value + "е пряме посилання на нову картинку.",
                                        parse_mode='HTML')
        return UPDATE_IMAGE
    else:
        await query.message.reply_text(message_error_field_doesnt_exist,
                                        parse_mode='HTML')
        return update_start(update, context)


async def update_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_value = update.message.text
    character = context.user_data['character']

    await collection.find_one_and_update({'id': character['id']},
                                         {'$set': {context.user_data['selected_field']: new_value}})

    await update.message.reply_text("<b>" + message_success_image_updated + "</b>",
                                    parse_mode = 'HTML')

    return ConversationHandler.END


async def update_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    new_value = query.data
    character = context.user_data['character']

    await collection.find_one_and_update({'id': character['id']},
                                         {'$set': {context.user_data['selected_field']: new_value}})

    await query.message.reply_text("<b>" + message_success_image_updated + "</b>",
                                    parse_mode = 'HTML')

    return ConversationHandler.END


async def update_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    new_value = query.data.split(" ")[0]
    character = context.user_data['character']

    await collection.find_one_and_update({'id': character['id']},
                                         {'$set': {context.user_data['selected_field']: new_value}})

    await query.message.reply_text("<b>" + message_success_image_updated + "</b>",
                                    parse_mode = 'HTML')

    return ConversationHandler.END


async def update_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_value = update.message.text
    character = context.user_data['character']

    try:
        urllib.request.urlopen(context.user_data['image_url'])

        await collection.find_one_and_update({'id': character['id']},
                                             {'$set': {context.user_data['selected_field']: new_value}})

        await update.message.reply_text("<b>" + message_success_image_updated + "</b>",
                                        parse_mode='HTML')

        return ConversationHandler.END
    except:
        await update.message.reply_text(message_error_incorrect_image_url)
        return await update_start(update, context)

###
#
# ВИДАЛЕННЯ
#
###

###
#
# СКАСУВАННЯ
#
###
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Скасування додавання"""
    await update.message.reply_text(message_notice_action_cancelled,
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Хендлер покрокового додавання картинки
conversation_handler_adding = ConversationHandler(
    entry_points=[CommandHandler('upload', upload_start)],
    states={
        SET_IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_image)],
        SET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
        SET_TITLE: [CallbackQueryHandler(set_title)],
        SET_EVENT: [CallbackQueryHandler(set_event)],
        SET_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_tags)],
        ADD_TO_DATABASE: [CallbackQueryHandler(add_to_database)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

# Хендлер покрокового редагування картинки
conversation_handler_updating = ConversationHandler(
    entry_points=[CommandHandler('update', update_start)],
    states={
        SET_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_field)],
        SET_NEWVALUE: [CallbackQueryHandler(set_newvalue)],
        UPDATE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_text)],
        UPDATE_TITLE: [CallbackQueryHandler(update_event)],
        UPDATE_EVENT: [CallbackQueryHandler(update_event)],
        UPDATE_IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_image)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

application.add_handler(conversation_handler_adding)
application.add_handler(CommandHandler('upload', upload_start))
application.add_handler(conversation_handler_updating)
application.add_handler(CommandHandler('update', upload_start))
application.run_polling()

