from django.core.cache import cache

def get_black_list():
    return cache.get("black_list", set())


def add_to_black_list(item):
    with cache.lock("black_list_lock"):
        black_list = get_black_list()
        black_list.add(item)
        cache.set("black_list", black_list)


def remove_from_black_list(item):
    with cache.lock("black_list_lock"):
        black_list = get_black_list()
        black_list.discard(item)
        cache.set("black_list", black_list)