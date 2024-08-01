from .solscan_parser import SolscanParser
from .models import SolscanResult

if __name__ == "__main__":
    address = "6eVtK4SdrkQVE84WLRGH5ydUrq29LE1b2U38MMX5xs4k"

    with SolscanParser(address) as parser:
        result: SolscanResult = parser.get_parse_result()
        print(result.temp_text)