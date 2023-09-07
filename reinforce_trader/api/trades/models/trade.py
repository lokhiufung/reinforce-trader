from typing import List, Optional
from pydantic import BaseModel, Field

# Define a Pydantic model for the Trade
class Trade(BaseModel):
    id: Optional[str] = Field(None, alias='_id')  # The alias='_id' allows you to use 'id' in Python but '_id' when interacting with MongoDB
    strategy: str
    ticker: str
    price: float
    tradeDate: str
    tradeSize: float
    tradeSide: int
    image: Optional[bytes] = None
    tradeNotes: Optional[str] = None

    class Config:
        allow_population_by_field_name = True  # This allows using the '_id' field to populate 'id'
