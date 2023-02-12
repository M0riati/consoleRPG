from items.consumable import Consumable
from items.stackableItem import StackableItem


class Inventory:
    def __init__(self):
        self.nonStackables = []
        self.stackables = []

    def addItem(self, item):
        if isinstance(item, StackableItem):
            for stack in self.stackables:
                if stack.__class__ == item.__class__:
                    stack.amount += item.amount
                    return
            self.stackables.append(item)
        else:
            self.nonStackables.append(item)

    @property
    def consumables(self):
        result = []
        for stack in self.stackables:
            if isinstance(stack, Consumable):
                result.append(stack)
        return result
