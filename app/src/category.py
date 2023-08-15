from dataclasses import dataclass
from typing import List
from product import Product


@dataclass
class Category:
    name: str
    description: str
    products: List[Product] = None
