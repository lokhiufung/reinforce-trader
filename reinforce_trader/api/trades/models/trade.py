from typing import List, Optional
from pydantic import BaseModel, Field

# Define a Pydantic model for the Trade
class Trade(BaseModel):
    id: Optional[str] = Field(None, alias='_id')  # The alias='_id' allows you to use 'id' in Python but '_id' when interacting with MongoDB
    userId: str
    strategy: str
    ticker: str
    price: float
    date: str
    size: float
    side: int
    image: Optional[bytes] = None
    notes: Optional[str] = None

    class Config:
        allow_population_by_field_name = True  # This allows using the '_id' field to populate 'id'
