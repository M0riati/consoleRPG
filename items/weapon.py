from character import *
from items.equipable import *
import ability
from util import *


def addSign(value):
    return f'+{value}' if value >= 0 else str(value)


class WeaponProperty:
    def __init__(self):
        pass

    def onAttack(self, target):
        pass

    def onHit(self, target):
        pass

    def __repr__(self):
        return 'I am broken so very very broken'


class DamageProperty(WeaponProperty):
    def __init__(self, dice, dmgType):
        super().__init__()
        self.dice = Dice(dice)
        self.type = dmgType

    def __repr__(self):
        return f'{self.dice.getMin()}-{self.dice.getMax()} ({self.dice}), {self.type.name.title()}'


class CriticalThreatProperty(WeaponProperty):
    def __init__(self, lvl, multiplier):
        super().__init__()
        self.lvl = lvl
        self.multiplier = multiplier

    def __repr__(self):
        return f'Critical Threat: {str(20 - self.lvl) + "-" if self.lvl > 0 else ""}{20}, x{self.multiplier}'


class HandednessProperty:
    def __init__(self, twoHanded=False, oneHandedModifier=0, offHandedModfier=0):
        super().__init__()
        self.twoHanded = twoHanded
        self.duelWieldModifier = oneHandedModifier
        self.offHandedModifier = offHandedModfier

    def __repr__(self):
        description = ''

        if self.duelWieldModifier != 0:
            description += f'{addSign(self.duelWieldModifier)} attack when dual wielding\n'

        if self.offHandedModifier != 0:
            description += f'{addSign(self.offHandedModifier)} attack when used in off-hand\n'

        if self.twoHanded:
            description += 'Two-Handed'
        else:
            description += 'One-Handed'
        return description


class DebuffProperty(WeaponProperty):
    def __init__(self, buff, chance, duration, dc):
        super().__init__()
        self.buff = buff
        self.chance = chance
        self.duration = duration
        self.dc = dc

    def onHit(self, target):
        if random.random() < self.chance:
            if not doAttributeCheck(target.constitution, self.dc):
                target.applyStatus(self.buff)

    def __repr__(self):
        return f'On hit: {round(self.chance * 100)}% chance of inflicting {self.buff.name} for {self.duration}s (DC{self.dc})'


class Weapon(Equipable):
    baseProperties = [

    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Weapon'
        self.desc = 'A weapon usually represents an equipable item that requires a hand slot and harms creatures.'
        self.attacks = 1

    def doDamageRoll(self, crit=False):
        damageBundle = DamageBundle()
        noRolls = 1 if not crit else self.critMultiplier
        for p in self.properties:
            if isinstance(p, DamageProperty):
                damageBundle.addDamage(Damage(p.dice.roll(times=noRolls), p.type))
        return damageBundle

    @property
    def attackMod(self):
        mod = 0
        for p in self.properties:
            if isinstance(p, HandednessProperty):
                if self.equippedInOffHand:
                    mod += p.offHandedModifier
                if self.character.duelWielding:
                    mod += p.duelWieldModifier
            elif isinstance(p, AttributeModifierProperty):
                mod += p.attack
        for ability_ in self.character.abilities:
            if isinstance(ability_, ability.Skill):
                for p in ability_.properties:
                    if isinstance(p, ability.WeaponProficiencyProperty):
                        if isinstance(self, p.weaponType):
                            mod += p.bonus
        if self.character.duelWielding:
            mod += self.character.duelWieldingModifiers[1] if self.equippedInOffHand else \
                self.character.duelWieldingModifiers[0]
        return mod

    @property
    def criticalRange(self):
        critLevel = 1
        for p in self.properties:
            if isinstance(p, CriticalThreatProperty):
                critLevel += p.lvl
        return list(range(20, 20 - critLevel, -1))

    @property
    def critMultiplier(self):
        currentMax = 0
        for p in self.properties:
            if isinstance(p, CriticalThreatProperty):
                currentMax = p.multiplier if p.multiplier > currentMax else currentMax
        return currentMax

    @property
    def twoHanded(self):
        for p in self.properties:
            if isinstance(p, HandednessProperty):
                return p.twoHanded
        return False

    @property
    def equippedInOffHand(self):
        return self.character.offHand == self

    def __repr__(self):
        return self.name

    @property
    def propertyDesc(self):
        propsToString = [str(prop) for prop in self.properties]
        result = []
        for prop in propsToString:
            result += prop.split('\n')
        return result

    def getFullDesc(self):
        return f'{self.name}\n\t{self.desc} \n\n\t' + '\n\t'.join([str(prop) for prop in self.properties])


class Warhammer(Weapon):
    baseProperties = [
        DamageProperty('3d10', DamageTypes.BLUDGEONING),
        HandednessProperty(True),
        CriticalThreatProperty(0, 2),
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Warhammer'
        self.desc = 'Large and heavy, the warhammer\'s design philosophy is just as well-defined as its appearance - basically trying to put as much momentum in a strike as possible to maximise blunt-force damage.'


class Mace(Weapon):
    baseProperties = [
        DamageProperty('2d8', DamageTypes.BLUDGEONING),
        HandednessProperty(False, -4),
        CriticalThreatProperty(0, 2),
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Mace'
        self.desc = 'Initially developed for piercing through plate armor, the mace is an accurate and hard hitting blunt weapon'


class MorningStar(Weapon):
    baseProperties = [
        DamageProperty('2d4', DamageTypes.BLUDGEONING),
        DamageProperty('1d5', DamageTypes.PIERCING),
        HandednessProperty(False, -4),
        CriticalThreatProperty(0, 2),
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Morning Star'
        self.desc = 'Similar to a mace, but with spikes on top, making it even more deadly.'


class Spear(Weapon):
    baseProperties = [
        DamageProperty('6d4', DamageTypes.PIERCING),
        HandednessProperty(True),
        CriticalThreatProperty(0, 2),
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Spear'
        self.desc = 'Combining decent damage with substantial reach, the spear enjoys widespread use.'


class Sword(Weapon):
    pass


class Shortsword(Sword):
    baseProperties = [
        DamageProperty('4d4', DamageTypes.SLASHING),
        CriticalThreatProperty(1, 2),
        HandednessProperty(False, 0, 2)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Shortsword'
        self.desc = 'A short sword.'


class Wakizashi(Sword):
    baseProperties = [
        DamageProperty('2d6', DamageTypes.SLASHING),
        CriticalThreatProperty(2, 3),
        HandednessProperty(False, 0, 2)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Wakizashi'
        self.desc = 'A one-edged shortsword of foreign design with the purpose of being used as a sidearm.'


class Katana(Sword):
    baseProperties = [
        DamageProperty('2d10', DamageTypes.SLASHING),
        CriticalThreatProperty(2, 3),
        HandednessProperty(False)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Katana'
        self.desc = 'A one-edged blade of foreign design whose capabilities are often overestimated. Still, a well-forged Katana can turn out to be a deadly weapon.'


class ArmingSword(Sword):
    baseProperties = [
        DamageProperty('5d4', DamageTypes.SLASHING),
        CriticalThreatProperty(1, 2),
        HandednessProperty(False)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Arming Sword'
        self.desc = 'The \'normal\' sword. Having a decently lengthed blade, it is aimed to be used in one hand while holding a shield in the other.'


class BastardSword(Sword):
    baseProperties = [
        DamageProperty('4d6', DamageTypes.SLASHING),
        CriticalThreatProperty(1, 2),
        HandednessProperty(False, -2)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Bastard Sword'
        self.desc = 'Sometimes referred to as the \'hand-and-a-half\' sword, the Bastard Sword is a shorter long sword which can also be, with a bit of effort, used in one hand.'


class Longsword(Sword):
    baseProperties = [
        DamageProperty('4d8', DamageTypes.SLASHING),
        CriticalThreatProperty(1, 2),
        HandednessProperty(True)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Longsword'
        self.desc = 'As the name might suggest, the long sword is the longer brother of the more usual arming sword. Because of its weight, it is wielded in both hands most of the time.'


class Greatsword(Sword):
    baseProperties = [
        DamageProperty('2d20', DamageTypes.SLASHING),
        CriticalThreatProperty(0, 2),
        HandednessProperty(True)
    ]

    def __init__(self, properties=[]):
        super().__init__(properties)
        self.name = 'Greatsword'
        self.desc = 'Heavy, imposing and as tall as a man, the greatsword combines deadly reach with powerful swings. On the other hand, it is so heavy its use needs proper training and conditioning.'


swords = [Shortsword, ArmingSword, BastardSword, Longsword, Greatsword]
