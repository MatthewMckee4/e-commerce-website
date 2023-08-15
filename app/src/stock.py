from dataclasses import dataclass, field
from typing import Dict
from product import Product


@dataclass
class Stock:
    products: Dict[Product, int] = field(default_factory=dict)

    def remove_product(self, product, quantity=1):
        if product in self.products:
            if self.products[product] >= quantity:
                self.products[product] -= quantity
                if self.products[product] == 0:
                    del self.products[product]
            else:
                raise ValueError("Insufficient stock")

    def remove_product(self, product, quantity=1):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")

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
