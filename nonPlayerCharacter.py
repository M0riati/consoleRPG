from random import choice

from character import Character
from items import Shortsword
from namegen import generateCharacterName


def randomNPC(lvl, hasWeapons=True):
    character = NonPlayerCharacter(generateCharacterName(), lvl=lvl)
    character.attributePointsRemaining += 3 * (character.level - 1)
    for x in range(0, character.attributePointsRemaining):
        character.spendAttributePoint(choice(['str', 'tgh', 'dex', 'wis', 'intl']))
    if hasWeapons:
        character.mainHand = Shortsword()
    return character


class NonPlayerCharacter(Character):
    def turn(self, fight):
        self.attack(self.getRandomTarget())
        return False

class Dummy(Character):
    def __init__(self):
        super().__init__(lvl=100, name='Test Dummy')

    def turn(self, fight):
        return False