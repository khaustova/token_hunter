from dataclasses import dataclass
from os import getenv

@dataclass
class SolanaConfig:
    api_key: str = getenv("HELIUS_API_KEY")
    
@dataclass
class Configuration:
    solana = SolanaConfig
    
configuration = Configuration()