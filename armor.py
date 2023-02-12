from items.item import Item


class Armor(Item):
    def __init__(self, malus, minDef, maxDef, resistances):
        super().__init__()
        self.malus = malus
        self.minDef = minDef
        self.maxDef = maxDef
        self.resistances = resistances
