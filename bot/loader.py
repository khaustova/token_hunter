from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis
from bot.configuration import configuration

redis = Redis(
    host=configuration.redis.host, 
    port=int(configuration.redis.port), 
    db=0
)
storage = RedisStorage(redis=redis)

dp = Dispatcher(storage=storage)
bot = Bot(token=configuration.bot.token)