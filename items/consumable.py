from items.item import *
from items.stackableItem import StackableItem
from util.usedOn import UsedOn


class Consumable(StackableItem):
    baseProperties = [

    ]

    def __init__(self, amount):
        self.usedOn = UsedOn.FRIENDLY
        super().__init__(amount)


class OnConsumeProperty(ItemProperty):
    def __init__(self, onConsume=lambda character: exec('pass')):
        self.onConsume = onConsume
