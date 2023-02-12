from items.consumable import *


def medpackHeal(character):
    character.heal(100)


class Potion(Consumable):
    baseProperties = [
        OnConsumeProperty(medpackHeal)
    ]

    def __init__(self, amount):
        super().__init__(amount)
        self.name = 'Potion'
        self.desc = 'Heals 100HP'
