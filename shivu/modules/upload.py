import urllib.request
from pymongo import ReturnDocument

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, sudo_users, collection, db, CHARA_CHANNEL_ID, SUPPORT_CHAT

WRONG_FORMAT_TEXT = "❌️ Некоректний формат!\nФормат: <code>/upload</code> <i>посилання_на_картинку ім'я-няшки назва-аніме подія трансліт-імені</i>\n\nІм'я няші, назву аніме та транслітерацію писати через дефіс, наприклад:\n<code>/upload</code> <i>посилання-на-картинку махіро-ояма мій-братик-вже-не-братик! 8 mahiro-oyama</i>\n\nПодія вказується відповідним числом. Транслітерацію імені вказувати англійською."

async def get_next_sequence_number(sequence_name):
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

# Код додавання няшок у бота
async def upload(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text(f"⚠️ Зверніться до одного з адмінів бота у {SUPPORT_CHAT}, щоби додати цю картинку.")
        return
    try:
        args = context.args
        if len(args) != 5:
            await update.message.reply_text(WRONG_FORMAT_TEXT, parse_mode = 'HTML')
            return

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()
        character_name_translit = args[4].replace('-', ' ').title()

        try:
            urllib.request.urlopen(args[0])
        except:
            await update.message.reply_text("❌️ Некоректне посилання. Радимо спочатку завантажити картинку на Imgur та вставляти пряме посилання звідти.")
            return

#        rarity_map = {
#                     1: "⚪️ Звичайна", 
#                     2: "🟣 Рідкісна", 
#                     3: "🟡 Легендарна", 
#                     4: "🔴 Міфічна"
#                     }
#        try:
#            rarity = rarity_map[int(args[3])]
#        except KeyError:
#            await update.message.reply_text("""❌️ Неправильна рідкість. Оберіть рідкість з нижченаведених варіантів:
#                                                1 : ⚪️ Звичайна
#                                                2 : 🟣 Рідкісна
#                                                3 : 🟡 Легендарна
#                                                4 : 🔴 Міфічна""")
#            return

        event_map =  {
                     1: "🐾 Твариноподібна", 
                     2: "👘 Східна", 
                     3: "🎉 Знаменна", 
                     4: "🐰 Великодня",
                     5: "🧑🏻‍🤝‍🧑🏻 Парна",
                     6: "🌈 Статезмінна",
                     7: "🏖️ Пляжна",
                     8: "🧹 Покоївкова",
                     9: "👩‍🏫 Шкільна",
                     10: "🎃 Геловінська",
                     11: "🍔 Гамбургерна",
                     12: "🎄 Різдвяна",
                     13: "Звичайна"
                     }
        try:
            event = event_map[int(args[3])]
        except KeyError:
            await update.message.reply_text("""❌️ Неправильна подія. Вкажіть подію, залежно від місяця:
                                                1 (січень): 🐾 Твариноподібна
                                                2 (лютий): 👘 Східна
                                                3 (березень): 🎉 Знаменна
                                                4 (квітень): 🐰 Великодня
                                                5 (травень): 🧑🏻‍🤝‍🧑🏻 Парна
                                                6 (червень): 🌈 Статезмінна
                                                7 (липень): 🏖️ Пляжна
                                                8 (серпень): 🧹 Покоївкова
                                                9 (вересень): 👩‍🏫 Шкільна
                                                10 (жовтень): 🎃 Геловінська
                                                11 (листопад): 🍔 Гамбургерна
                                                12 (грудень): 🎄 Різдвяна
                                                13 : Звичайна""")
            return

        id = str(await get_next_sequence_number('character_id')).zfill(2)

        character = {
            'img_url': args[0],
            'name': character_name,
            'name_translit': character_name_translit,
            'anime': anime,
#           'rarity': rarity,
            'event': event,
            'id': id
        }

        # Виведення інформації про додавання в канал Хапайки
        try:
            message = await context.bot.send_photo(
                chat_id = CHARA_CHANNEL_ID,
                photo = args[0],
                caption = f"<b>Няшка:</b> {character_name} - {id}\n<b>Транслітерація імені:</b> {character_name_translit}\n<b>Тайтл:</b> {anime}\n<b>Подія:</b> {event}\n\nДодано користувачем <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode = 'HTML'
            )
            character['message_id'] = message.message_id
            await collection.insert_one(character)
            await update.message.reply_text("✅ Няшку успішно додано!")
        except:
            await collection.insert_one(character)
            update.effective_message.reply_text("⚠️ Няшку додано, однак не знайдено Telegram-каналу бази даних.")
        
    except Exception as e:
        await update.message.reply_text(f"❌️ Не вдалося завантажити няшку. Помилка: {str(e)}\nЯкщо ви вважаєте, що помилка в коді, зверніться до адмінів бота у {SUPPORT_CHAT}")

# Код видалення няшок з бота
async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text(f"⚠️ Зверніться до одного з адмінів бота у {SUPPORT_CHAT}, щоби видалити цю картинку.")
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌️ Неправильний формат! Формат: <code>/delete</code> <i>ID</i>")
            return
        
        character = await collection.find_one_and_delete({'id': args[0]})

        if character:
            
            await context.bot.delete_message(chat_id = CHARA_CHANNEL_ID, message_id = character['message_id'])
            await update.message.reply_text("✅ ГОТОВО")
        else:
            await update.message.reply_text("✅ Няшку успішно видалено з бази даних, але не знайдено в каналі.")
    except Exception as e:
        await update.message.reply_text(f'{str(e)}')

# Код оновлення няшок в боті
async def update(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text(f"⚠️ Зверніться до одного з адмінів бота у {SUPPORT_CHAT}, щоби оновити цю картинку.")
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("❌️ Неправильний формат! Формат: <code>/update</code> <i>id поле нове_значення<i>")
            return

        # шукаємо няшку за ID
        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text("❌️ Няшку не знайдено.")
            return

        # перевіряємо, чи поле валідне
        valid_fields = ['img_url', 'name', 'name_translit', 'anime', 'event']
        if args[1] not in valid_fields:
            await update.message.reply_text(f"❌️ Неправильно вказане поле. Будь ласка, оберіть одне з наступних: {', '.join(valid_fields)}.")
            return

        # змінюємо поле
        if args[1] in ['name', 'name_translit', 'anime']:
            new_value = args[2].replace('-', ' ').title()
       # elif args[1] == 'rarity':
       #     rarity_map = {
       #              1: "⚪️ Звичайна", 
       #              2: "🟣 Рідкісна", 
       #              3: "🟡 Легендарна", 
       #              4: "🔴 Міфічна",
       #              5: "💮 Особлива"
       #              }
       #     try:
       #         new_value = rarity_map[int(args[2])]
       #     except KeyError:
       #         await update.message.reply_text("""❌️ Неправильна рідкість. Оберіть рідкість з нижченаведених варіантів:
       #                                         1 : ⚪️ Звичайна
       #                                         2 : 🟣 Рідкісна
       #                                         3 : 🟡 Легендарна
       #                                         4 : 🔴 Міфічна
       #                                         5 : 💮 Особлива""")
       #         return
        elif args[1] == 'event':
            event_map =  {
                     1: "🐾 Твариноподібна", 
                     2: "👘 Східна", 
                     3: "🧨 Знаменна", 
                     4: "🐰 Великодня",
                     5: "🧑🏻‍🤝‍🧑🏻 Парна",
                     6: "🌈 Статезмінна",
                     7: "🏖️ Пляжна",
                     8: "🧹 Покоївкова",
                     9: "👩‍🏫 Шкільна",
                     10: "🎃 Геловінська",
                     11: "🍔 Гамбургерна",
                     12: "🎄 Різдвяна",
                     13: "Звичайна"
                     }
            try:
                new_value = event_map[int(args[2])]
            except KeyError:
                await update.message.reply_text("""❌️ Неправильна подія. Вкажіть подію, залежно від місяця:
                                                1 (січень): 🐾 Твариноподібна
                                                2 (лютий): 👘 Східна
                                                3 (березень): 🧨 Знаменна
                                                4 (квітень): 🐰 Великодня
                                                5 (травень): 🧑🏻‍🤝‍🧑🏻 Парна
                                                6 (червень): 🌈 Протилежна
                                                7 (липень): 🏖️ Пляжна
                                                8 (серпень): 🧹 Покоївкова
                                                9 (вересень): 👩‍🏫 Шкільна
                                                10 (жовтень): 🎃 Геловінська
                                                11 (листопад): 🍔 Гамбургерна
                                                12 (грудень): 🎄 Різдвяна
                                                13 : Звичайна""")
                return
        else:
            new_value = args[2]

        await collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

# Виведення інформації про оновлення в канал Хапайки
        # якщо міняється картинка
        if args[1] == 'img_url':
            await context.bot.delete_message(chat_id = CHARA_CHANNEL_ID, message_id = character['message_id'])
            message = await context.bot.send_photo(
                chat_id = CHARA_CHANNEL_ID,
                photo = new_value,
                caption = f"<b>Няшка:</b> {character_name} - {id}\n<b>Транслітерація імені:</b> {character_name_translit}\n<b>Тайтл:</b> {anime}\n<b>Подія:</b> {event}\n\nОновлено користувачем <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode = 'HTML'
            )
            character['message_id'] = message.message_id
            await collection.find_one_and_update({'id': args[0]}, {'$set': {'message_id': message.message_id}})
        # якщо міняється щось інше
        else:           
            await context.bot.edit_message_caption(
                chat_id = CHARA_CHANNEL_ID,
                message_id = character['message_id'],
                caption = f"<b>Няшка:</b> {character_name} - {id}\n<b>Транслітерація імені:</b> {character_name_translit}\n<b>Тайтл:</b> {anime}\n<b>Подія:</b> {event}\n\nОновлено користувачем <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode = 'HTML'
            )

        await update.message.reply_text("✅ Завершено оновлення в базі даних. Однак іноді потрібен час, щоби оновити опис у вашому чаті, тому зачекайте.")
    except Exception as e:
        await update.message.reply_text(f"❌️ Схоже, бота не додано до чату, або такої няшки не існує, або неправильний id няшки.")

UPLOAD_HANDLER = CommandHandler('upload', upload, block = False)
application.add_handler(UPLOAD_HANDLER)
DELETE_HANDLER = CommandHandler('delete', delete, block = False)
application.add_handler(DELETE_HANDLER)
UPDATE_HANDLER = CommandHandler('update', update, block=False)
application.add_handler(UPDATE_HANDLER)
