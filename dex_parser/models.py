from datetime import datetime
from pydantic import BaseModel


class DEXResult(BaseModel):
    date: datetime = datetime.now()
    address: str = ""
    temp_text: str = ""