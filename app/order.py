from dataclasses import dataclass
from typing import List
from user import User


@dataclass
class Order:
    user: User
    items: List[tuple]  # List of ordered items (product, quantity pairs)
    total_cost: float
    shipping_address: str
    status: str = "Pending"
