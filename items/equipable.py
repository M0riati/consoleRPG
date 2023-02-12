from items.item import *


class Equipable(Item):
    baseProperties = [

    ]

    def __init__(self, properties=[]):
        super().__init__(properties=[])
        self.name = 'Equipable'
        self.desc = 'An item that can be equipped.'
        self.character = None


class EquipableProperty(ItemProperty):
    pass


class AttributeModifierProperty(EquipableProperty):
    def __init__(self, strg=0, dex=0, const=0, intl=0, wis=0, attack=0):
        self.strength = strg
        self.dexterity = dex
        self.constitution = const
        self.intelligence = intl
        self.wisdom = wis
        self.attack = attack

    def __repr__(self):
        description = ''
        if self.strength > 0:
            description += f'+{self.strength} Strength \n'
        elif self.strength < 0:
            description += f'{self.strength} Strength \n'

        if self.dexterity > 0:
            description += f'+{self.dexterity} Dexterity \n'
        elif self.dexterity < 0:
            description += f'{self.dexterity} Dexterity \n'

        if self.constitution > 0:
            description += f'+{self.constitution} Constitution \n'
        elif self.constitution < 0:
            description += f'{self.constitution} Constitution \n'

        if self.intelligence > 0:
            description += f'+{self.intelligence} Intelligence \n'
        elif self.intelligence < 0:
            description += f'{self.intelligence} Intelligence \n'

        if self.wisdom > 0:
            description += f'+{self.wisdom} Wisdom \n'
        elif self.wisdom < 0:
            description += f'{self.wisdom} Wisdom \n'

        if self.attack > 0:
            description += f'+{self.attack} Attack \n'
        elif self.attack < 0:
            description += f'{self.attack} Attack \n'

        return description
