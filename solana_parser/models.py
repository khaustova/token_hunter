from datetime import datetime
from pydantic import BaseModel


class SolscanResult(BaseModel):
    date: datetime = datetime.now()
    address: str = ""
    temp_text: str = ""