from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    image_url: str
    stock_quantity: int = 0
    category: str = None
