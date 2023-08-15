from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Product:
    id: int
    name: str
    description: str
    price: float
    image_url: str
    category: str = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Product) and self.id == other.id
