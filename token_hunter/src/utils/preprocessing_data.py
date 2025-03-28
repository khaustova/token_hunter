import logging

logger = logging.getLogger(__name__)


def clear_number(number_str: str) -> float | int:
    """Преобразует переданную строку в число, удаляя лишние символы и обрабатывая значения с "K" и "M".

    Args:
        number_str: Строка, содержащая число.

    Returns:
        Преобразованное число. В случае ошибки возвращает -1.
    """
    number_str = number_str.lstrip("$")
    number_str = (
        number_str
        .replace(",", "")
        .replace(">", "")
        .replace("<", "")
        .replace("$", "")
        .replace(" ", "")
        .replace("%", "")
        .replace("+", "")
        .replace("₄", "00")
        .replace("₅", "000")
    )
    try:
        if number_str[-1] == "K":
            number_str = number_str[:-1]
            number = float(number_str) * 1000
        elif number_str[-1] == "M":
            number_str = number_str[:-1]
            number = float(number_str) * 1000000
        else:
            number = float(number_str)
    except Exception:
        number = -1

    return number


def get_pnl(bought_str: str, sold_str: str) -> list | None:
    """Вычисляет список значений PNL на основе данных о покупках и продажах.

    Args:
        bought_str: Строка, содержащая суммы покупок, разделённые пробелами.
        sold_str: Строка, содержащая суммы продаж, разделённые пробелами.

    Returns:
        Список значений PNL. В случае ошибки возвращает None.
    """
    try:
        bought_lst = [float(x) for x in bought_str.split(" ")]
        sold_lst = [float(x) for x in sold_str.split(" ")]
        pnl_lst = [sold - bought if sold else 0 for bought, sold in zip(bought_lst, sold_lst)]
        return pnl_lst
    except Exception:
        return None


def count_pnl_loss(bought_str: str, sold_str: str) -> int | None:
    """Подсчитывает количество отрицательных значений PNL (убытков).

    Args:
        bought_str: Строка, содержащая суммы покупок, разделённые пробелами.
        sold_str: Строка, содержащая суммы продаж, разделённые пробелами.

    Returns:
        Количество отрицательных значений PNL. В случае ошибки возвращает None.
    """
    try:
        pnl_lst = get_pnl(bought_str, sold_str)
        pnl_loss = sum(i < 0 for i in pnl_lst)
        return pnl_loss
    except Exception:
        return None
        

def get_sum_of_operation(num_str: str) -> float | None:
    """Вычисляет общую сумму операций (покупок или продаж) на основе переданной строки.

    Args:
        num_str: Строка, содержащая суммы операций, разделённые пробелами.

    Returns:
        Общая сумма операций. В случае ошибки возвращает None.
    """
    try:
        num_lst = [float(x) for x in num_str.split(" ")]
        num_sum = sum(num_lst)
        return num_sum
    except Exception:
        return None


def count_no_operation(num_str: str) -> int | None:
    """Подсчитывает количество операций без покупки или продажи (нулевые значения).

    Args:
        num_str: Строка, содержащая суммы операций, разделённые пробелами.

    Returns:
        Количество нулевых операций. В случае ошибки возвращает None.
    """
    try:
        num_lst = [float(x) for x in num_str.split(" ")]
        count_zero = num_lst.count(0)
        return count_zero
    except Exception:
        return None


def get_text_list_element_by_index(lst: list, ind: int) -> str:
    """Возвращает текст элемента списка по указанному индексу.

    Args:
        lst: Список, из которого извлекается элемент.
        ind: Индекс элемента.

    Returns:
        Текст элемента списка или "0", если элемент не существует.
    """
    try:
        result = lst[ind].text
    except Exception:
        result = "0"
        logger.debug("Не удалось получить текст элемента по индексу %d", ind)

    return result
