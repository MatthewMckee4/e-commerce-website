from dataclasses import dataclass
from typing import List
from order import Order


@dataclass
class User:
    username: str
    email: str
    password_hash: str
    shipping_address: str
    order_history: List[Order] = None
