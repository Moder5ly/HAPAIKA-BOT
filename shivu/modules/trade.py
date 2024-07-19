from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shivu import user_collection, shivuu

pending_trades = {}


@shivuu.on_message(filters.command("trade"))
async def trade(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("❌️ Потрібно відповісти на повідомлення користувача, аби обмінятися няшками!")
        return

    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await message.reply_text("❌️ Із собою не можна обмінюватися!")
        return

    if len(message.command) != 3:
        await message.reply_text("❌️ Потрібно надати ID обох няшок!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    sender = await user_collection.find_one({'id': sender_id})
    receiver = await user_collection.find_one({'id': receiver_id})

    sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
    receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

    if not sender_character:
        await message.reply_text("❌️ У вас немає персонажа, якого ви намагаєтесь обміняти!")
        return

    if not receiver_character:
        await message.reply_text("❌️ У іншого користувача немає персонажа, на якого ви намагаєтесь виміняти!")
        return

    if len(message.command) != 3:
        await message.reply_text("/trade [ID вашого персонажа] [ID персонажа іншого користувача]!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]
    
    pending_trades[(sender_id, receiver_id)] = (sender_character_id, receiver_character_id)
   
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Підтвердити", callback_data = "confirm_trade")],
            [InlineKeyboardButton("❌️ Скасувати", callback_data = "cancel_trade")]
        ]
    )

    await message.reply_text(f"{message.reply_to_message.from_user.mention}, чи приймаєте ви цей обмін?", reply_markup = keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_trade", "cancel_trade"]))
async def on_callback_query(client, callback_query):
    receiver_id = callback_query.from_user.id

    for (sender_id, _receiver_id), (sender_character_id, receiver_character_id) in pending_trades.items():
        if _receiver_id == receiver_id:
            break
    else:
        await callback_query.answer("❌️ Це не ваш обмін!", show_alert = True)
        return

    if callback_query.data == "confirm_trade":       
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
        receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

        sender['characters'].remove(sender_character)
        receiver['characters'].remove(receiver_character)
  
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})
    
        sender['characters'].append(receiver_character)
        receiver['characters'].append(sender_character)

        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text(f"✅ Обмін із {callback_query.message.reply_to_message.from_user.mention} успішно проведено!")

    elif callback_query.data == "cancel_trade":
        del pending_trades[(sender_id, receiver_id)]
        await callback_query.message.edit_text("❌️ Обмін скасовано....")

pending_gifts = {}

@shivuu.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("❌️ Потрібно відповісти на повідомлення користувача, аби подарувати няшками!")
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_username = message.reply_to_message.from_user.username
    receiver_first_name = message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await message.reply_text("❌️ Із собою не можна обмінюватися!")
        return

    if len(message.command) != 2:
        await message.reply_text("❌️ Потрібно надати ID няшки!")
        return

    character_id = message.command[1]

    sender = await user_collection.find_one({'id': sender_id})

    character = next((character for character in sender['characters'] if character['id'] == character_id), None)

    if not character:
        await message.reply_text("❌️ У твоїй колекції немає такого персонажа!")
        return

    character_name = character['name']
    
    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name
    }

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Підтвердити", callback_data = "confirm_gift")],
            [InlineKeyboardButton("❌️ Скасувати", callback_data = "cancel_gift")]
        ]
    )

    await message.reply_text(f"Ви бажаєте подарувати {character_name} користувачеві {message.reply_to_message.from_user.mention}?", reply_markup = keyboard)

@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_gift", "cancel_gift"]))
async def on_callback_query(client, callback_query):
    sender_id = callback_query.from_user.id
   
    for (_sender_id, receiver_id), gift in pending_gifts.items():
        if _sender_id == sender_id:
            break
    else:
        await callback_query.answer("❌️ Це не ваш дарунок!", show_alert = True)
        return

    if callback_query.data == "confirm_gift":
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender['characters'].remove(gift['character'])
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})

        if receiver:
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': gift['character']}})
        else:
            
            await user_collection.insert_one({
                'id': receiver_id,
                'username': gift['receiver_username'],
                'first_name': gift['receiver_first_name'],
                'characters': [gift['character']],
            })
 
        del pending_gifts[(sender_id, receiver_id)]

        await callback_query.message.edit_text(f"✅ Ви успішно подарували няшку користувачеві [{gift['receiver_first_name']}](tg://user?id={receiver_id})!")
