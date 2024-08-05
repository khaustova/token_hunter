import asyncio
import logging
from solana_parser.solana_parser import SolanaParser
from logger.logger import get_logger

log_level: str = "DEBUG"
logging.basicConfig(level=log_level)

async def main():
    address = "36zP5mXM9uRzAc2bh23hE3Dd8VuGy1N97eFwAEe5W9BC"
    solana = SolanaParser(mode="Open")
    result = solana.get_first_buy_transactions(5, address)
    for res in result:
        print(res)


if __name__ == "__main__":
    asyncio.run(main())