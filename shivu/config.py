class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "342536463"
    sudo_users = "342536463", "5977032096", "6759307389"
    GROUP_ID = -1002106637387
    TOKEN = "7234685639:AAE4bBqx65TeD-zM2RIOOala17wkEFy38EY"
    mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "hurtivka"
    UPDATE_CHAT = "hurtivka"
    BOT_USERNAME = "waifulove_bot"
    CHARA_CHANNEL_ID = "-1002106637387"
    api_id = 28177306
    api_hash = "363c71a849c8f6117d66b15d110264a6"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
