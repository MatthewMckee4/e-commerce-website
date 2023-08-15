from dataclasses import dataclass, field
from typing import Dict
from product import Product


@dataclass
class Stock:
    products: Dict[Product, int] = field(default_factory=dict)

    def add_product(self, product, quantity):
        if product in self.products:
            self.products[product] += quantity
        else:
            self.products[product] = quantity

    def remove_product(self, product, quantity):
        if product in self.products:
            if self.products[product] >= quantity:
                self.products[product] -= quantity
                if self.products[product] == 0:
                    del self.products[product]
            else:
                raise ValueError("Insufficient stock")

    def get_stock_quantity(self, product):
        return self.products.get(product, 0)

    def check_stock_availability(self, product, quantity):
        return self.get_stock_quantity(product) >= quantity


# Example usage:

# Create some products
product1 = Product(
    1,
    "Product 1",
    "Description of Product 1",
    19.99,
    "product1.jpg",
    stock_quantity=50,
    category="Electronics",
)
product2 = Product(
    2,
    "Product 2",
    "Description of Product 2",
    29.99,
    "product2.jpg",
    stock_quantity=100,
    category="Clothing",
)

#
