from typing import List, Optional
from pydantic import BaseModel, Field

# # Define a Pydantic model for the Trade
# class Strategy(BaseModel):
#     id: Optional[str] = Field(None, alias='_id')  # The alias='_id' allows you to use 'id' in Python but '_id' when interacting with MongoDB
#     userId: str
#     name: str
#     initialCash: float
#     cash: float

#     class Config:
#         allow_population_by_field_name = True  # This allows using the '_id' field to populate 'id'


class Strategy(BaseModel):
    name: str
    initialCash: float
    # stopLoss: float
    # takeProfit: float
    # prob: float = 0.3  # probability of winning


class StrategyUpdate(BaseModel):
    name: str=None
    initialCash: float=None
    # stopLoss: float
    # takeProfit: float
    # prob: float = 0.3  # probability of winning
