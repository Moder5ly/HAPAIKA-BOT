class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "342536463"
    sudo_users = "342536463"
    GROUP_ID = -1002106637387
    TOKEN = "7234685639:AAE4bBqx65TeD-zM2RIOOala17wkEFy38EY"
    mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "hurtivka"
    UPDATE_CHAT = "hurtivka"
    BOT_USERNAME = "waifulove_bot"
    CHARA_CHANNEL_ID = "-1002133191051"
    api_id = 26626068
    api_hash = "bf423698bcbe33cfd58b11c78c42caa2"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
