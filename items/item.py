class Item:
    baseProperties = [

    ]

    def __init__(self, properties=[]):
        self.name = 'Item'
        self.desc = 'Something.'
        self.properties = self.__class__.baseProperties + properties


class ItemProperty:
    pass
