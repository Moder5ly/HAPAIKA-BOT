class Config(object):
    LOGGER = True

    # ці значення отримати з my.telegram.org/apps
    api_id = 28177306
    api_hash = "363c71a849c8f6117d66b15d110264a6"

    # тег і API-токен бота
    BOT_USERNAME = "hapaika_bot"
    API_TOKEN = "7325552038:AAER11O3ZVBcgBu29BUhvj2Dof9paAaoWfc"

    # база даних бота
    mongo_url = ("mongodb+srv://moder5ly:n64o3qsMyxvsSywY@cluster0.cjksadk.mongodb.net/"
                 "?retryWrites=true&w=majority&appName=Cluster0")

    # картинки бота
    PHOTO_URL = ["https://i.ibb.co/D5DhBVD/art1.png",
                 "https://i.ibb.co/0Y3Mmjs/art2.png",
                 "https://i.ibb.co/GkzhG94/art3.png"]

    # ID власника бота
    OWNER_ID = "342536463"

    # ID адмінів бота
    SUDO_USERS_ID = ("342536463",
                     "5977032096",
                     "6759307389")

    # чат-лог про нових юзерів
    GROUP_ID = -1002028115983
    CHARA_CHANNEL_ID = "-1002028115983"

    # чат підтримки юзерів
    SUPPORT_ID = "HapaikaJudgment"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
