import asyncio
import logging
from solana_parser.solana_parser import SolanaParser
from logger.logger import get_logger
import time
import asyncio
from solana.rpc.api import Client
from typing import Optional
from helius import TransactionsAPI
from solders.signature import Signature
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from configuration import configuration
from logger.logger import get_logger

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com/" 
SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"

logger = get_logger(__name__)

log_level: str = "DEBUG"
logging.basicConfig(level=log_level)

async def main():
    address = "36zP5mXM9uRzAc2bh23hE3Dd8VuGy1N97eFwAEe5W9BC"
    client = Client(SOLANA_RPC_URL, timeout=50)
    signature = Signature.from_string("4HTePE6qz1TfmTBGRfFnLLZhT5S5czb3DoPg9nf6VAMa8yhNQ9J1jNBvU5zeEpAyJadV2tKK9ZK45ptdcizqtL9u")
    transaction = client.get_transaction(signature, encoding="jsonParsed", max_supported_transaction_version=0)
    solana = SolanaParser()
    print(solana.get_open_transaction_info(signature))
    # result = solana.get_first_buy_transactions(5, address)
    # for res in result:
    #     print(res)


if __name__ == "__main__":
    asyncio.run(main())