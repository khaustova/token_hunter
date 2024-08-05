from solana.rpc.api import Client
import time
import asyncio
import base64
from solana.rpc.async_api import AsyncClient
from typing import Optional
from solders.signature import Signature
from solders.pubkey import Pubkey

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com/"

async def get_oldest_transaction_signature(address: str) -> Optional[str]:
    async with AsyncClient(SOLANA_RPC_URL, timeout=50) as client:
        i = 0
        before = None
        oldest_signature = None

        address = Pubkey.from_string(address)

        while True:
            signatures_response = await client.get_signatures_for_address(
                address, before=before, limit=1000
            )
            signatures = signatures_response.value
            if not signatures:
                signature_str = str(oldest_signature)
                old_s = "639YAPvhkaTbkTf2m6bEeWuw3Z36gnu8m9sUMBXPNj41xTQmX7k4SC1XDMW6un3mLWSHeJbbPqCzumSqRrqCSFYu"
                signature = Signature.from_string(signature_str)
                #prev_s = Signature.from_string(prev_signature)
                tx_detail_response = await client.get_transaction(signature, encoding="jsonParsed", max_supported_transaction_version=0)
                prev_tr = await client.get_transaction(prev_signature, encoding="jsonParsed", max_supported_transaction_version=0)
                tx_detail = tx_detail_response.value
                try:
                    with open("last.txt", "w") as file:
                        file.write(str(tx_detail))
                    with open("prev.txt", "w") as file:
                        file.write(str(prev_tr.value))
                    #print(tx_detail)
                    #print(prev_tr.value)
                except Exception as e:
                    print(f"Error parsing transaction details: {e}")
                break  # No more signatures found
            # Update the oldest signature
            oldest_signature = signatures[-1].signature
            prev_signature = signatures[-2].signature
            time.sleep(5)
            i += 1
            print(f"шаг {i}")
            # Set the 'before' parameter to the oldest signature in the current batch
            before = oldest_signature
        return str(oldest_signature)


async def main():
    address = "5Mbqo6CWrXSXuaJnd1s699oqB4upGP7oenVDQjzeLGvv"
    oldest_signature = await get_oldest_transaction_signature(address)
    print(f"Oldest Transaction Signature: {oldest_signature}")


if __name__ == "__main__":
    asyncio.run(main())