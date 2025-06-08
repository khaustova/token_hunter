import json
import time
import base58
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from solders.keypair import Keypair


def sign_message(wallet: Keypair, message: str) -> dict:
    """Signs a message using a Solana wallet.

    Args:
        wallet: Solana Keypair instance for message signing.
        message: Message string to be signed.

    Returns:
        dict: Signature dictionary in the format:
            {
                "data": list[int],  # signature as byte array
                "type": "ed25519"   # signature algorithm type
            }
    """
    message_bytes = message.encode("utf-8")
    signature = wallet.sign_message(message_bytes)
    signature_base58 = str(signature)
    signature_data = list(base58.b58decode(signature_base58))

    return {
        "data": signature_data,
        "type": "ed25519",
    }


def login_to_rugcheck(wallet: Keypair) -> None:
    """Authenticates with RugCheck API using Solana wallet.

    Args:
        wallet: Solana Keypair instance for authentication.

    Raises:
        Exception: If there's an error making the request to RugCheck API.
    """
    message_data = {
        "message": "Sign-in to Rugcheck.xyz",
        "timestamp": int(time.time() * 1000),
        "publicKey": str(wallet.pubkey()),
    }
    message_json = json.dumps(message_data, separators=(",", ":"))

    signature = sign_message(wallet, message_json)

    payload = {
        "signature": signature,
        "wallet": str(wallet.pubkey()),
        "message": message_data,
    }

    try:
        response = requests.post(
            "https://api.rugcheck.xyz/auth/login/solana",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        if response.status_code == 200:
            response_data = response.json()
            print("Login successful:", response_data)
        else:
            print("Failed to login:", response.status_code, response.text)
    except Exception as e:
        print("Failed to login", e)


class Command(BaseCommand):
    """Django management command for RugCheck API authentication."""

    help = "Authenticates with RugCheck API using Solana wallet"

    def handle(self, *args, **kwargs) -> None:
        wallet = Keypair.from_base58_string(settings.SOLANA_PRIVATE_KEY)
        login_to_rugcheck(wallet)

