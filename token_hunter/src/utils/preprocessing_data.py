import logging

logger = logging.getLogger(__name__)


def clear_number(number_str: str) -> float | int:
    """Converts a string to a number by removing extra characters and handling 'K'/'M' suffixes.

    Args:
        number_str: String containing a number value.

    Returns:
        Converted number. Returns -1 on error.
    """
    if not number_str:
        return -1

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
    """Calculates PNL values based on buy and sell amounts.

    Args:
        bought_str: String containing space-separated buy amounts.
        sold_str: String containing space-separated sell amounts.

    Returns:
        List of PNL values. Returns None on error.
    """
    try:
        bought_lst = [float(x) for x in bought_str.split(" ")]
        sold_lst = [float(x) for x in sold_str.split(" ")]
        pnl_lst = [sold - bought if sold else 0 for bought, sold in zip(bought_lst, sold_lst)]
        return pnl_lst
    except Exception:
        return None


def count_pnl_loss(bought_str: str, sold_str: str) -> int | None:
    """Counts the number of negative PNL values (losses).

    Args:
        bought_str: String containing space-separated buy amounts.
        sold_str: String containing space-separated sell amounts.

    Returns:
        Count of negative PNL values. Returns None on error.
    """
    try:
        pnl_lst = get_pnl(bought_str, sold_str)
        pnl_loss = sum(i < 0 for i in pnl_lst)
        return pnl_loss
    except Exception:
        return None
        

def get_sum_of_operation(num_str: str) -> float | None:
    """Calculates the total sum of operations (buys or sells) from a string.

    Args:
        num_str: String containing space-separated operation amounts.

    Returns:
        Total sum of operations. Returns None on error.
    """
    try:
        num_lst = [float(x) for x in num_str.split(" ")]
        num_sum = sum(num_lst)
        return num_sum
    except Exception:
        return None


def count_no_operation(num_str: str) -> int | None:
    """Counts the number of zero-value operations (no buys/sells).

    Args:
        num_str: String containing space-separated operation amounts.

    Returns:
        Count of zero-value operations. Returns None on error.
    """
    try:
        num_lst = [float(x) for x in num_str.split(" ")]
        count_zero = num_lst.count(0)
        return count_zero
    except Exception:
        return None


def get_text_list_element_by_index(lst: list, ind: int) -> str:
    """Returns the text of a list element at the specified index.

    Args:
        lst: List to get element from.
        ind: Element index.

    Returns:
        Element text or "0" if element doesn't exist.
    """
    try:
        result = lst[ind].text
    except Exception:
        result = "0"
        logger.debug("Failed to get text for element at index %d", ind)

    return result
