from solana.rpc.api import Client
import time
import asyncio
import base64
from solana.rpc.async_api import AsyncClient
from typing import Optional
from solders.signature import Signature
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com/" 
SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"

async def get_oldest_transaction_signature(address: str) -> Optional[str]:
    async with AsyncClient(SOLANA_RPC_URL, timeout=50) as client:
        buy_signature = Signature.from_string("2Qym6KxxMBJvjxnzLTLEaNbX2QhQLgJn1XLuxNFMGQek9JRVz5chqFo7PHTMAJxYqTnBTSMts637oLArc76BMcUS")
        # Swap 0.01 ($1.7654) WSOL for 146,974.990494 ($1.738) CDWOG
        # signer: H25YTfnGhRUNdFixbZ5NDrfdZhodKS9RrRfXF9HR3Gyp
        buy_signature_2 = Signature.from_string("4Y6B6xJLiZsT1YgPJCw7xiYafBBZKJCjHBhMPEMXD2aaWhMdS6bPCikqxbmsUa3bLCsLqSzBK8mD69bynZt7ifek")
        # Swap 0.4 ($70.25) WSOL for 3,854,053.164859 ($24.33) CDWOG
        # signer: BSHNj3GDL2EvXbuGc1UMfXF8otBd82dMAtbV5iaiEm4L
        
        sell_signature = Signature.from_string("2cZyC8Um8wvxyD1k5eZbtkK94EjCWaWYspeYEyv9of7gGC2qkrBaDyFHLQ9tJyKLqjkJX7L8vsuwvXG23fY1TGJi")
        # Swap 275,063.321296 ($3.2527) CDWOG for 0.01858455 ($3.2809) WSOL
        # signer: 3LmdFtWeXTueQPcXKfQHt8rhZFWpXUYYVSwCZxmoGFAc
        sell_signature_2 = Signature.from_string("52Nvpq3fdu93p4Wnfgxb4cznUr7di1mCD1Ca4ZawT1BgAqSLUshsiEFAHi3fPVfPkocGfyUBbz5pg8x2Z5uEcXcK")
        # Swap 275,582.765085 ($1.7569) CDWOG for 0.009578468 ($1.6974) WSOL
        # signer: rUwxr2anE9qkBagd5oP2MxKwfAM1Lsshe21hShLir8M
        
        tx_buy = await client.get_transaction(buy_signature, encoding="jsonParsed", max_supported_transaction_version=0)

        time.sleep(5)
       
        tx_sell = await client.get_transaction(sell_signature, encoding="jsonParsed", max_supported_transaction_version=0)
        
        time.sleep(5)
        
        tx_buy_2 = await client.get_transaction(buy_signature_2, encoding="jsonParsed", max_supported_transaction_version=0)
        
        time.sleep(5)
        
        tx_sell_2 = await client.get_transaction(sell_signature_2, encoding="jsonParsed", max_supported_transaction_version=0)
        
        await get_transaction_info(tx_buy)
        await get_transaction_info(tx_buy_2)
        await get_transaction_info(tx_sell)
        await get_transaction_info(tx_sell_2)
        

async def get_transaction_info(transaction: GetTransactionResp):
    result = {}
    result["who"] = str(transaction.value.transaction.transaction.message.account_keys[0].pubkey)
    result["type"] = await get_transaction_type(transaction)
    
    for ui_instruction in transaction.value.transaction.meta.inner_instructions:
        for instruction in ui_instruction.instructions:
            try:
                if instruction.parsed.get("type") == "transfer":
                    amount = instruction.parsed.get("info").get("amount")
                    if amount:
                        authority = instruction.parsed.get("info").get("authority")
                        if authority == result["who"]: 
                            if result["type"] == "buy":
                                result["sol"] = amount
                            else:
                                result["coin"] = amount
                        else:
                            if result["type"] == "buy":
                                result["coin"] = amount
                            else:
                                result["sol"] = amount
            except:
                continue 
    
    print(result)


async def get_transaction_type(transaction: GetTransactionResp):
    
    for token in transaction.value.transaction.meta.pre_token_balances:
        if str(token.mint) == SOLANA_TOKEN_ADDRESS:
            pre_sol_balance = token.ui_token_amount.amount
            break
            
    for token in transaction.value.transaction.meta.post_token_balances:
        if str(token.mint) == SOLANA_TOKEN_ADDRESS:
            post_sol_balance = token.ui_token_amount.amount
            break
            
    if int(pre_sol_balance) - int(post_sol_balance) <= 0:
        return "buy"
    
    return "sell"


async def main():
    address = "5Mbqo6CWrXSXuaJnd1s699oqB4upGP7oenVDQjzeLGvv"
    oldest_signature = await get_oldest_transaction_signature(address)

if __name__ == "__main__":
    asyncio.run(main())
    
# with open("buy_buy.txt", "w") as file:
#     file.write(str(tx_buy_2.value))
# with open("sell_sell.txt", "w") as file:
#     file.write(str(tx_sell_2.value))