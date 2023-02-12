from items.item import Item


class StackableItem(Item):
    def __init__(self, amount):
        super().__init__()
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if value < 1:
            del self
            return
        self._amount = value

    def __repr__(self):
        return f'{self.name} (x{self.amount})'
