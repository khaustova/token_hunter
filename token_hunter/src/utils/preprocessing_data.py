import logging

logger = logging.getLogger(__name__)


def clear_number(number_str: str) -> float:
    """
    Преобразует переданную строку в число, удаляя лишние символы и 
    обрабатывая значения с "K" и "M".
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
    except Exception as e:
        logger.error("Ошибка преобразования строки в число")
        number = None
    
    return number


def get_pnl(bought_str: str, sold_str: str) -> list:
    """
    Возвращает список PNL.
    """
    try:
        bought_lst = [float(x) for x in bought_str.split(" ")]
        sold_lst = [float(x) for x in sold_str.split(" ")]
        pnl_lst = [sold - bought if sold else 0 for bought, sold in zip(bought_lst, sold_lst)]
        
        return pnl_lst
    except:
        return
    

def count_pnl_loss(bought_str: str, sold_str: str) -> int:
    """
    Возвращает количество отрицательных PNL.
    """
    
    try:
        pnl_lst = get_pnl(bought_str, sold_str)
        pnl_loss = sum(i < 0 for i in pnl_lst)
        
        return pnl_loss
    except:
        return 
        

def get_sum_of_operation(num_str: str) -> float:
    """
    Вовзращает общую сумму покупок или продаж.
    """
    
    try:
        num_lst = [float(x) for x in num_str.split(" ")]
        num_sum = sum(num_lst)
        
        return num_sum
    except:
        return


def count_no_operation(num_str: str) -> int:
    """
    Возвращает количество операций без покупки или продажи.
    """
    
    try:
        num_lst = [float(x) for x in num_str.split(" ")]
        count_zero = num_lst.count(0)
        
        return count_zero
    except:
        return
