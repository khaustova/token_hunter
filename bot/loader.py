from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, Redis
from configuration import configuration

if configuration.redis.is_redis:
    redis = Redis(
        host=configuration.redis.host, 
        port=configuration.redis.port, 
        db=0
    )
    storage = RedisStorage(redis=redis)
else:
    storage = MemoryStorage()

dp = Dispatcher(storage=storage)
bot = Bot(token=configuration.bot.token)