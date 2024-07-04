import urllib.request
from pymongo import ReturnDocument

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, sudo_users, collection, db, CHARA_CHANNEL_ID, SUPPORT_CHAT

WRONG_FORMAT_TEXT = """❌️ Некоректний формат! 
Формат: /upload посилання_на_картинку ім'я-няшки назва-аніме рідкість

Ім'я няші та назву аніме писати через дефіс. Рідкість вказувати відповідною цифрою:

1 (⚪️ Звичайна)
2 (🟣 Рідкісна)
3 (🟡 Легендарна)
4 (🔴 Міфічна)"""



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

async def upload(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('⚠️ Запитай у власника.')
        return

    try:
        args = context.args
        if len(args) != 4:
            await update.message.reply_text(WRONG_FORMAT_TEXT)
            return

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        try:
            urllib.request.urlopen(args[0])
        except:
            await update.message.reply_text('❌️ Некоректне посилання.')
            return

        rarity_map = {1: "⚪️ Звичайна", 2: "🟣 Рідкісна", 3: "🟡 Легендарна", 4: "🔴 Міфічна"}
        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            await update.message.reply_text('❌️ Неправильна рідкість. Оберіть 1, 2, 3 або 4 рідкість.')
            return

        id = str(await get_next_sequence_number('character_id')).zfill(2)

        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'id': id
        }

        try:
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=args[0],
                caption=f"<b>Ім'я няшки:</b> {character_name}\n<b>Тайтл:</b> {anime}\n<b>Рідкість:</b> {rarity}\n<b>ID:</b> {id}\nДодано користувачем <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
            await collection.insert_one(character)
            await update.message.reply_text('✅ Няшку додано!')
        except:
            await collection.insert_one(character)
            update.effective_message.reply_text("⚠️ Няшку додано, однак не знайдено каналу бази даних.")
        
    except Exception as e:
        await update.message.reply_text(f'❌️ Не вдалося завантажити няшку. Помилка: {str(e)}\nЯкщо ви думаєте, що помилка в коді, зверніться до: {SUPPORT_CHAT}')

async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('⚠️ Попросіть власника скористатися цією командою.')
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text('❌️ Неправильний формат! Формат: /delete ID')
            return

        
        character = await collection.find_one_and_delete({'id': args[0]})

        if character:
            
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            await update.message.reply_text('✅ ГОТОВО')
        else:
            await update.message.reply_text('✅ Няшку успішно видалено з бази даних, але не знайдено в каналі.')
    except Exception as e:
        await update.message.reply_text(f'{str(e)}')

async def update(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('⚠️ Вам не дозволено користуватися цією командою.')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('❌️ Неправильний формат! Формат: /update id поле нове_значення')
            return

        # Get character by ID
        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text('❌️ Няшку не знайдено.')
            return

        # Check if field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if args[1] not in valid_fields:
            await update.message.reply_text(f'❌️ Неправильно вказане поле. Будь ласка, оберіть одне з наступних: {", ".join(valid_fields)}.')
            return

        # Update field
        if args[1] in ['name', 'anime']:
            new_value = args[2].replace('-', ' ').title()
        elif args[1] == 'rarity':
            rarity_map = {1: "⚪️ Звичайна", 2: "🟣 Рідкісна", 3: "🟡 Легендарна", 4: "🔴 Міфічна", 5: "💮 Особлива"}
            try:
                new_value = rarity_map[int(args[2])]
            except KeyError:
                await update.message.reply_text('❌️ Неправильна рідкість. Оберіть 1, 2, 3, 4 або 5 рідкість.')
                return
        else:
            new_value = args[2]

        await collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

        
        if args[1] == 'img_url':
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=new_value,
                caption=f"<b>Ім'я няшки:</b> {character['name']}\n<b>Тайтл:</b> {character['anime']}\n<b>Рідкість:</b> {character['rarity']}\n<b>ID:</b> {character['id']}\nОновлено користувачем <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
            await collection.find_one_and_update({'id': args[0]}, {'$set': {'message_id': message.message_id}})
        else:
            
            await context.bot.edit_message_caption(
                chat_id=CHARA_CHANNEL_ID,
                message_id=character['message_id'],
                caption=f"<b>Ім'я няшки:</b> {character['name']}\n<b>Тайтл:</b> {character['anime']}\n<b>Рідкість:</b> {character['rarity']}\n<b>ID:</b> {character['id']}\nОновлено користувачем <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a>",
                parse_mode='HTML'
            )

        await update.message.reply_text('✅ Завершено оновлення в базі даних. Однак іноді потрібен час, щоби оновити опис у вашому чаті, тому зачекайте.')
    except Exception as e:
        await update.message.reply_text(f'❌️ Схоже, бота не додано до чату, або такої няшки не існує, або неправильний id няшки.')

UPLOAD_HANDLER = CommandHandler('upload', upload, block=False)
application.add_handler(UPLOAD_HANDLER)
DELETE_HANDLER = CommandHandler('delete', delete, block=False)
application.add_handler(DELETE_HANDLER)
UPDATE_HANDLER = CommandHandler('update', update, block=False)
application.add_handler(UPDATE_HANDLER)
