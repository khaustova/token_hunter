from redis import Redis

redis = Redis(db=1)


def get_redis_set(name: str) -> set[str]:
    """Retrieves all elements from a Redis set, decodes them from bytes to strings,
    and returns as a Python set.

    Args:
        name: Redis key where the set is stored.

    Returns:
        Set of strings. Returns empty set if the key doesn't exist.
    """
    return {item.decode() for item in redis.smembers(name)}


def add_to_redis_set(name: str, item: str) -> None:
    """Adds an element to a Redis set under the specified key.

    Args:
        name: Redis key where the set is stored.
        item: Element to add to the set. 
              Will be automatically converted to string before storing.
    """
    redis.sadd(name, str(item))


def remove_from_redis_set(name: str, item: str) -> None:
    """Removes an element from a Redis set under the specified key.

    Args:
        name: Redis key where the set is stored.
        item: Element to remove from the set.
              Will be automatically converted to string before removal.
    """
    redis.srem(name, str(item))
