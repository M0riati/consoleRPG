import random

from util.damageTypes import *


def rollD20():
    return Dice('1d20').roll()


def getAttributeMod(attribute):
    return attribute // 2 - 5


def doModifierCheck(modifier, dc):
    return rollD20() + modifier >= dc


def doAttributeCheck(attribute, dc):
    return rollD20() + getAttributeMod(attribute) >= dc


class Dice:
    def __init__(self, dice: str):
        d = 0
        dice = dice.lower()
        for char in dice:
            if (char not in 'd0123456789') or (char == 'd' and d > 0):
                raise ValueError('The dice roll is not denoted in the correct format')
            elif char == 'd':
                d += 1
        split = dice.split('d')
        self.numberOfDice = int(split[0])
        self.sides = int(split[1])

    def roll(self, times=1):
        return sum([random.randint(1, self.sides) for _ in range(0, self.numberOfDice * times)])

    def getMin(self):
        return self.numberOfDice

    def getMax(self):
        return self.numberOfDice * self.sides

    def __repr__(self):
        return f'{self.numberOfDice}d{self.sides}'


class Damage:
    def __init__(self, amount, dmgType):
        self.amount = amount
        self.type = dmgType

    def __mul__(self, other):
        if isinstance(other, float):
            self.amount = round(self.amount * other)
        return self

    def deal(self, target, log=True):
        target.harm(self.amount, self.type)
        if log:
            if self.amount > 0:
                target.fight.combatLog.append(f'Dealing {self.amount} {self.type.name.lower()} damage to {target}')
            elif self.type != DamageTypes.UNSTOPPABLE:
                target.fight.combatLog.append(f'No damage dealt.')

    def convert(self, dmgType):
        self.type = dmgType


class DamageBundle:
    def __init__(self, bundle=None):
        if bundle is None:
            bundle = [Damage(0, DamageTypes.UNSTOPPABLE)]
        self.contents = bundle

    def addDamage(self, damage):
        self.contents.append(damage)

    def deal(self, target):
        for dmg in self.contents:
            dmg.deal(target)

    def convert(self, dmgType):
        for dmg in self.contents:
            dmg.convert(dmgType)

    def __mul__(self, other):
        if isinstance(other, float):
            for damage in self.contents:
                damage *= other
        return self
