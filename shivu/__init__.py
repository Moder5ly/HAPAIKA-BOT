import logging  
from pyrogram import Client
from telegram.ext import Application
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

from config import Development as Config

BOT_USERNAME = Config.BOT_USERNAME
API_TOKEN = Config.API_TOKEN

PHOTO_URL = Config.PHOTO_URL

OWNER_ID = Config.OWNER_ID
sudo_users = Config.SUDO_USERS_ID

GROUP_ID = Config.GROUP_ID
CHARA_CHANNEL_ID = Config.CHARA_CHANNEL_ID

SUPPORT_ID = Config.SUPPORT_ID

# канал, куди шлються оновлення
# бота та нові картинки
UPDATE_CHANNEL = "hapaika_channel"

# запуск бота
application = Application.builder().token(API_TOKEN).build()
bot = Client("Hapaika", Config.api_id, Config.api_hash, bot_token=API_TOKEN)

# підключення до МонгоДБ
connect_db = AsyncIOMotorClient(Config.mongo_url)
database = connect_db['Hapaika']

# таблиця усіх персонажів
db_character_cards = database['character_cards']
# таблиця колекцій користувачів
db_user_collections = database['user_collections']

# таблиця к-сті карток для виведення топу гравців у групі
db_group_user_totals = database['group_user_totals']
# таблиця кастомних значень повідомлень на випадання у чатах
db_message_frequencies = database['group_message_frequencies']

# таблиця користувачів, які користувалися ботом
db_users = database['total_pm_users']
# таблиця топу груп за к-стю карток (ПРИБРАТИ)
db_top_global_groups = database['top_global_groups']