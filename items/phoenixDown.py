from items import Consumable, OnConsumeProperty
from util.usedOn import UsedOn


def phoenixDownRevive(character):
    character.revive(0.25)


class PhoenixDown(Consumable):
    baseProperties = [
        OnConsumeProperty(phoenixDownRevive)
    ]

    def __init__(self, amount):
        super().__init__(amount)
        self.name = 'Phoenix Down'
        self.desc = 'Revives and refreshes 25% HP'
        self.usedOn = UsedOn.DEAD
