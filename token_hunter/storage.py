from redis import Redis

redis = Redis(db=1)


def get_redis_set(name: str) -> set:
    """Возвращает все элементы множества из Redis, декодирует их из байтов в строки
    и возвращает как множество Python.

    Args:
        name: Ключ Redis, по которому хранится множество.

    Returns:
        Множество строк. Если ключ не существует, возвращает пустое множество.
    """
    return {item.decode() for item in redis.smembers(name)}


def add_to_redis_set(name: str, item: str) -> None:
    """Добавляет элемент в множество Redis по указанному ключу.

    Args:
        name: Ключ Redis, по которому хранится множество.
        item: Элемент для добавления в множество. 
            Будет автоматически преобразован в строку перед сохранением.
    """
    redis.sadd(name, str(item))


def remove_from_redis_set(name: str, item: str) -> None:
    """Удаляет элемент из множества Redis по указанному ключу.

    Args:
        name: Ключ Redis, по которому хранится множество.
        item: Элемент для удаления из множества. 
            Будет автоматически преобразован в строку перед удалением.
    """
    redis.srem(name, str(item))
