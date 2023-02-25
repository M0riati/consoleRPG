from ability import *
from asciimatics.screen import Screen
from items import *
from status import *
from util import *

STANDARD_DUEL_WIELDING_MODS = (-6, -10)


class Character:

    def __init__(self, name, strg=10, dex=10, const=10, intl=10, wis=10, lvl=1, attPtsRem=10, skillPtsRem=10):
        self.name = name
        self.level = lvl
        self.exp = 0
        self.attributePointsRemaining = attPtsRem
        self.skillPointsRemaining = skillPtsRem
        self.inventory = Inventory()
        self.maxHP = 9999
        self.maxMP = 9999
        self.hp = self.maxHP
        self.mp = self.maxMP
        self.abilities = [skilltreeRoot]
        self.justLearnt = []
        self.statusEffects = []
        self.equippedWeapons = []
        self.armor = None
        self.initiative = 0
        self._mainHand = None
        self._offHand = None
        self.armor = None
        self.baseStrength = strg
        self.baseConstitution = const
        self.baseDexterity = dex
        self.baseIntelligence = intl
        self.baseWisdom = wis
        self.timeOfLastAttack = 0
        self.resultOfLastAttack = ''
        self.baseTypeModifiers = {

        }
        self.updateHP()
        self.updateMP()
        self.fight = None

    @property
    def availableAbilities(self):
        available = []
        for ability_ in self.abilities:
            for learnableAbility in ability_.dependents:
                if learnableAbility not in available and learnableAbility not in self.abilities:
                    available.append(learnableAbility)
        return available

    @property
    def castableSpells(self):
        elligible = []
        for ability_ in self.abilities:
            if isinstance(ability_, Castable):
                elligible.append(ability_)
        return elligible

    def learn(self, skill):
        if skill in self.availableAbilities and self.skillPointsRemaining > 0:
            self.skillPointsRemaining -= 1
            self.justLearnt.append(skill)
            self.abilities.append(skill)

    @property
    def speedModifier(self):
        speedModifier = 1
        for status in self.statusEffects:
            if isinstance(status, SpeedModifyingStatus):
                speedModifier *= status.speedModifier
            if speedModifier == 0:
                break
        return speedModifier

    def unlearn(self, skill):
        if skill in self.justLearnt:
            for dependent in skill.dependents:
                self.unlearn(dependent)
            self.justLearnt.remove(skill)
            self.abilities.remove(skill)
            self.skillPointsRemaining += 1

    def confirmSkills(self):
        self.abilities += self.justLearnt
        self.justLearnt = []

    @property
    def strength(self):
        return self.baseStrength

    @property
    def constitution(self):
        return self.baseConstitution

    @property
    def dexterity(self):
        return self.baseDexterity

    @property
    def intelligence(self):
        return self.baseIntelligence

    @property
    def wisdom(self):
        return self.baseWisdom

    @property
    def ac(self):
        return 10 + getAttributeMod(self.dexterity) - (self.armor.malus if self.armor is not None else 0)

    @property
    def typeModifiers(self):
        return self.baseTypeModifiers

    def attackRoll(self, weapon_, target):
        weaponMod = weapon_.attackMod
        dexMod = getAttributeMod(self.dexterity)
        roll = rollD20() + dexMod + weaponMod - (10 if self.hasStatusOfType(Blind) else 0)
        hit = (roll >= target.ac)
        crit = limit(roll, 0, 20) in weapon_.criticalRange
        self.fight.combatLog.append(
            f'{self.name} rolls {roll} + {weaponMod} (Weapon Mod) + {dexMod} (Dex Mod) against {target} (AC{target.ac})')
        self.fight.combatLog.append(f'{"Miss!" if not (hit or crit) else "Hit!" if not crit else "Critical Hit!"}')
        return hit or crit, crit

    @property
    def duelWieldingModifiers(self):
        mainHandMod = STANDARD_DUEL_WIELDING_MODS[0]
        offHandMod = STANDARD_DUEL_WIELDING_MODS[1]
        for ability_ in self.abilities:
            if isinstance(ability_, Skill):
                for prop in ability_.properties:
                    if isinstance(prop, DuelWieldingModifierProperty):
                        mainHandMod += prop.mainHandMod
                        offHandMod += prop.offHandMod
        return mainHandMod, offHandMod

    @property
    def duelWielding(self):
        return self.offHand is not None and self.mainHand is not None and not self.mainHand.twoHanded

    @property
    def mainHand(self):
        return self._mainHand

    @property
    def offHand(self):
        return self._offHand

    @mainHand.setter
    def mainHand(self, newWeapon):
        if self._mainHand is None:
            if self._offHand is not None:
                self._offHand.character = None
                self._offHand = None
            if newWeapon.twoHanded:
                self._mainHand = self._offHand = newWeapon
            else:
                self._mainHand = newWeapon
        else:
            self._mainHand.character = None
            if newWeapon.twoHanded:
                if self._offHand is not None:
                    self._offHand.character = None
                self._mainHand = self._offHand = newWeapon
            else:
                if self._mainHand.twoHanded:
                    self._mainHand = self._offHand = None
                self._mainHand = newWeapon
        newWeapon.character = self

    def elligibleTargets(self, allied=False, allowReflect=True):
        if self in self.fight.party:
            return self.fight.enemies if not allied else filter(
                lambda i: i != self and not (i.hasStatusOfType(Reflect) and not allowReflect), self.fight.party)
        elif self in self.fight.enemies:
            return self.fight.party if not allied else filter(
                lambda i: i != self and not (i.hasStatusOfType(Reflect) and not allowReflect), self.fight.enemies)

    def getRandomTarget(self, allied=False):
        return choice(self.elligibleTargets(allied))

    def getWeakestTarget(self, allied=False):
        elligibleTargets = self.elligibleTargets(allied)
        currentLow = (0, elligibleTargets[0].hp)
        for i in range(0, len(elligibleTargets) - 1):
            hp = elligibleTargets[i].hp
            if hp < currentLow[1]:
                currentLow = (i, hp)
        return elligibleTargets[currentLow[1]]

    def getStrongestTarget(self, allied=False):
        elligibleTargets = self.elligibleTargets(allied)
        currentHigh = (0, elligibleTargets[0].hp)
        for i in range(0, len(elligibleTargets) - 1):
            hp = elligibleTargets[i].hp
            if hp > currentHigh[1]:
                currentHigh = (i, hp)
        return elligibleTargets[currentHigh[1]]

    @offHand.setter
    def offHand(self, newWeapon):
        if newWeapon.twoHanded:
            self.mainHand = newWeapon
            return
        if self._offHand is None:
            if self._mainHand is None:
                self._mainHand = newWeapon
            else:
                self._offHand = newWeapon
        else:
            if self._mainHand is None:
                self._mainHand = newWeapon
                self._offHand.character = None
                self._offHand = None
            elif self._mainHand.twoHanded:
                self._mainHand = newWeapon
                self._offHand.character = None
                self._offHand = None
            else:
                self._offHand = newWeapon
        newWeapon.character = self

    def consume(self, consumable):
        for p in consumable.properties:
            if isinstance(p, OnConsumeProperty):
                p.onConsume(self)
        self.fight.combatLog.append(f'{self.name} uses {consumable.name}')
        consumable.amount -= 1

    @property
    def dead(self):
        return self.hp == 0

    def revive(self, percentage=1):
        if self.dead:
            self.hp = percentage * self.maxHP
        elif self.hasStatusOfType(Zombified):
            self.hp = 0

    def harm(self, amount, dmgType=damageTypes.DamageTypes.UNSTOPPABLE, appliedZombification=False):
        if self.hasStatusOfType(Petrified):
            self.hp = 0
        if self.hasStatusOfType(Zombified) and not appliedZombification:
            self.heal(amount, appliedZombification=True)
            return
        if amount < 0:
            self.heal(-amount)
            return
        if dmgType in self.typeModifiers.keys():
            amount *= (1 + self.typeModifiers[dmgType])
        if self.hasStatusOfType(Shield) and dmgType in halvedByShield:
            amount *= 0.5
        elif self.hasStatusOfType(MagicalShield) and dmgType in halvedByMagicShield:
            amount *= 0.5
        if self.hasStatusOfType(BloodMarkHP) or self.hasStatusOfType(BloodMarkMP):
            for statusEffect in self.statusEffects:
                if isinstance(statusEffect, BloodMarkHP):
                    statusEffect.caster.heal(0.3*amount)
                elif isinstance(statusEffect, BloodMarkMP):
                    statusEffect.caster.modifyMP(0.6*amount)
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def hasStatusOfType(self, type_):
        for status in self.statusEffects:
            if isinstance(status, type_):
                return True
        return False

    def applyStatus(self, statusType, chance=1.0, dc=30, duration=None, caster=None):
        if random.random() <= chance:
            if not self.hasStatusOfType(statusType):
                if not doAttributeCheck(self.constitution, dc):
                    status = statusType(self, duration=duration, caster=caster)
                    self.statusEffects.append(status)
                    status.onApply()

    def update(self, delta):
        self.initiative += self.speedModifier * self.dexterity * delta * 5
        self.modifyMP(self.wisdom * delta)
        for status in self.statusEffects:
            status.effect(delta)

    def heal(self, amount, appliedZombification=False):
        if not self.dead:
            if self.hasStatusOfType(Zombified) and not appliedZombification:
                self.harm(amount, appliedZombification=True)
                return
            if amount < 0:
                self.harm(-amount)
                return
            self.hp += amount
            if self.hp > self.maxHP:
                self.hp = self.maxHP

    @property
    def uniqueWeapons(self):
        if self.mainHand is None:
            return None, None
        return (self.mainHand, self.offHand) if not self.mainHand.twoHanded else (self.mainHand,)

    def attack(self, target, multiplier=1.0, convertToDamageType=None, critGuaranteed=False):
        hitAtLeastOnce = False
        for weapon_ in self.uniqueWeapons:
            if weapon_ is None:
                continue
            for i in range(0, weapon_.attacks):
                isHit, isCrit = self.attackRoll(weapon_, target) if not critGuaranteed else True, True
                if isHit:
                    hitAtLeastOnce = True
                    if isCrit:
                        self.fight.combatLog.append(f'Rolling {weapon_.critMultiplier}x')
                        damage = weapon_.doDamageRoll(crit=True) * multiplier
                        if convertToDamageType is not None:
                            damage.convert(convertToDamageType)
                        damage.deal(target)
                    else:
                        damage = weapon_.doDamageRoll()
                        if convertToDamageType is not None:
                            damage.convert(convertToDamageType)
                        damage.deal(target)
        if target.hasStatusOfType(ShockBarrier):
            Damage(Dice('2d6').roll(), DamageTypes.LIGHTNING).deal(self)
            self.applyStatus(Stunned, 0.3, 20, 3)
        return hitAtLeastOnce

    def getHealthBar(self, width=10):
        bars = round(self.hpPercentage * width)
        return f'{round(self.hp)}/{self.maxHP} ]{bars * "■" + (width - bars) * " "}['

    def getMPBar(self, width=10):
        bars = round(self.mpPercentage * width)
        return f'{round(self.mp)}/{self.maxMP} ]{bars * "■" + (width - bars) * " "}['

    def getInitiativeBar(self, width=10):
        bars = round((self.initiative / 100) * width)
        return f']{bars * "■" + (width - bars) * " "}['

    def getBattleCharacterInfo(self, barWidth=15, turn=False):
        return [
            f'{self.name} (lvl{self.level}) {", ".join([status.name for status in self.statusEffects])}' + (
                '       <<' if turn else ''),
            f'HP: {self.getHealthBar(barWidth)}',
            f'MP: {self.getMPBar(barWidth)}',
            f'INIT: {self.getInitiativeBar(barWidth // 2)}',
            f'WEAPONS: {self.mainHand}{", " + self.offHand.name if self.offHand is not None and not self.offHand.twoHanded else ""}'
        ] if not self.dead else [
            (f'{self.name} (lvl{self.level})' + ('       <<' if turn else ''), Screen.COLOUR_MAGENTA),
            ('DEAD', Screen.COLOUR_MAGENTA),
            ('', Screen.COLOUR_MAGENTA),
            ('', Screen.COLOUR_MAGENTA),
            ('', Screen.COLOUR_MAGENTA),
        ]

    def lvlUP(self):
        self.exp = 0
        self.level += 1
        self.attributePointsRemaining += 3

    def lvlEXP(self):
        return 300 * (self.level + 1) ** 1.5

    def gainEXP(self, amount):
        self.exp += amount
        lvlEXP = self.lvlEXP()
        if self.exp > lvlEXP:
            expAtNextLevel = self.exp - lvlEXP
            self.lvlUP()
            self.gainEXP(expAtNextLevel)

    def updateHP(self):
        hpPercentage = self.hpPercentage
        self.maxHP = 10 * self.level * (5 + getAttributeMod(self.constitution))
        self.hp = hpPercentage * self.maxHP

    def updateMP(self):
        mpPercentage = self.mpPercentage
        self.maxMP = 5 * self.level * (5 + getAttributeMod(self.wisdom))
        self.mp = mpPercentage * self.maxMP

    def learnAllDependents(self, skilltreeNode):
        for dependent in skilltreeNode.dependents:
            self.abilities.append(dependent)
            self.learnAllDependents(dependent)

    @property
    def hpPercentage(self):
        return limit(self.hp / self.maxHP)

    @property
    def mpPercentage(self):
        return limit(self.mp / self.maxMP)

    def modifyMP(self, amount):
        self.mp += amount
        if self.mp > self.maxMP:
            self.mp = self.maxMP
        elif self.mp < 0:
            self.mp = 0
        if self.hasStatusOfType(HPConversion) and amount < 0:
            self.mp -= amount/2
            self.harm(-amount/4)

    def canUseSpell(self, spell):
        if spell in self.abilities:
            if not self.hasStatusOfType(HPConversion):
                return self.mp >= spell.mpCost and self.hp >= spell.hpCost
            else:
                return self.mp >= spell.mpCost/2 and self.hp >= spell.hpCost + spell.mpCost/4
        return False

    def turn(self, battle):
        return True

    def useAbility(self, ability_, target):
        if ability_ in self.abilities:
            ability_.cast(self, target)

    def spendAttributePoint(self, attribute):
        if self.attributePointsRemaining > 0:
            self.attributePointsRemaining -= 1
            if attribute == 'str':
                self.baseStrength += 1
            elif attribute == 'tgh':
                self.baseConstitution += 1
                self.updateHP()
            elif attribute == 'dex':
                self.baseDexterity += 1
            elif attribute == 'int':
                self.baseIntelligence += 1
            elif attribute == 'wis':
                self.baseWisdom += 1
                self.updateMP()
            else:
                self.attributePointsRemaining += 1

    def reclaimAttributePoint(self, attribute):
        self.attributePointsRemaining += 1
        if attribute == 'str' and self.strength > 8:
            self.baseStrength -= 1
        elif attribute == 'tgh' and self.constitution > 8:
            self.baseConstitution -= 1
            self.updateHP()
        elif attribute == 'dex' and self.dexterity > 8:
            self.baseDexterity -= 1
        elif attribute == 'int' and self.intelligence > 8:
            self.baseIntelligence -= 1
        elif attribute == 'wis' and self.wisdom > 8:
            self.baseWisdom -= 1
            self.updateMP()
        else:
            self.attributePointsRemaining -= 1

    def __repr__(self):
        return self.name
