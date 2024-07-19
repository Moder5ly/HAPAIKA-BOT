class Config(object):
    LOGGER = True

    # Ці значення отримати з my.telegram.org/apps
    api_id = 28177306
    api_hash = "363c71a849c8f6117d66b15d110264a6"
    # тег і API-токен бота
    BOT_USERNAME = "hapaika_bot"
    TOKEN = "7325552038:AAER11O3ZVBcgBu29BUhvj2Dof9paAaoWfc"
    # база даних бота
    mongo_url = "mongodb+srv://moder5ly:n64o3qsMyxvsSywY@cluster0.cjksadk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # картинки бота
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    # ID власника бота
    OWNER_ID = "342536463"
    # ID адмінів бота
    sudo_users = "342536463", "5977032096", "6759307389"
    # канал, куди надсилаються логи про додавання і оновлення няшок
    CHARA_CHANNEL_ID = "-1002224770278"
    # чат-лог про нових юзерів
    GROUP_ID = -2106637387
    # чат підтримки юзерів
    SUPPORT_CHAT = "hurtivka"
    # чат (канал?) куди шлються оновлення бота
    UPDATE_CHAT = "hurtivka"


class Production(Config):
    LOGGER = True

class Development(Config):
    LOGGER = True
