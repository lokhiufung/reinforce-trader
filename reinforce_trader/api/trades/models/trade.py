from typing import Optional

from pydantic import BaseModel

# Define a Pydantic model for the Trade
class Trade(BaseModel):
    # id: Optional[str] = Field(None, alias='_id')  # The alias='_id' allows you to use 'id' in Python but '_id' when interacting with MongoDB
    strategy: str
    ticker: str
    price: float
    date: str
    size: float
    side: int
    image: str
    notes: str

    # class Config:
    #     allow_population_by_field_name = True  # This allows using the '_id' field to populate 'id'

class TradeUpdate(BaseModel):
    strategy: Optional[str] = None
    ticker: Optional[str] = None
    price: Optional[float] = None
    date: Optional[str] = None
    size: Optional[float] = None
    side: Optional[int] = None
    image: Optional[str] = None
    notes: Optional[str] = None
