from dataclasses import dataclass
from typing import List


@dataclass
class Cart:
    items: List[tuple]  # List of cart items (product, quantity pairs)

    def add_item(self, product, quantity):
        # Add a product and quantity to the cart
        pass

    def update_item(self, product, quantity):
        # Update the quantity of a product in the cart
        pass

    def remove_item(self, product):
        # Remove a product from the cart
        pass

    def get_total(self):
        # Calculate the total cost of items in the cart
        pass
