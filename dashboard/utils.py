from typing import Callable


def order_items(original: list,
                reference: list,
                getter: Callable = lambda x: x
                ) -> list:
    """
    Возвращает список, упорядоченный в соответствии с расположением элементов 
    в списке-образце.
    """
    ordered_indexes = []
    for item in original:
        try:
            ind = reference.index(getter(item))
        except:
            ind = len(original)
        ordered_indexes.append(ind)

    return [y for x, y in sorted(zip(ordered_indexes, original), key=lambda x: x[0])]
