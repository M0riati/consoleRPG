from random import choice

from items import Sword
from status import *
from util import *
from util.usedOn import UsedOn

"""
An ability is something that a player can acquire through a Lvl-Up.
It unlocks a special attack or gives permanent bonuses.
"""


class Ability:
    def __init__(self, name='...', desc='I am broken so very very broken', lvlRequirement=0, dependents=None):
        if dependents is None:
            dependents = []
        self.name = name
        self.desc = desc
        self.lvlRequirement = lvlRequirement
        self.dependents = dependents

    def __repr__(self):
        return self.name


'''
Skills are passive abilities.
'''


class Skill(Ability):
    def __init__(self, name, desc, dependents, properties):
        super().__init__(name, desc, dependents)
        self.dependents = dependents
        self.properties = properties


class SkillProperty:
    def __init__(self):
        pass


class DuelWieldingModifierProperty(SkillProperty):
    def __init__(self, mainHandMod, offHandMod):
        super().__init__()
        self.mainHandMod = mainHandMod
        self.offHandMod = offHandMod


class WeaponProficiencyProperty(SkillProperty):
    def __init__(self, bonus, weaponType):
        super().__init__()
        self.bonus = bonus
        self.weaponType = weaponType


class Castable(Ability):
    def __init__(self, name, desc, dependents, oncast, mpCost, hpCost=0, usedOn=UsedOn.HOSTILE, repellable=False,
                 castableIfSilenced=True):
        super().__init__(name, desc, dependents)
        self.dependents = dependents
        self.mpCost = mpCost
        self.oncast = oncast
        self.hpCost = hpCost
        self.usedOn = usedOn
        self.repellable = repellable
        self.castableIfSilenced = castableIfSilenced

    def __repr__(self):
        return f'{self.name} ({self.mpCost} MP)'

    def cast(self, caster, target):
        if self.repellable and target.hasStatusOfType(Reflect):
            if target.hasStatusOfType(Reflect):
                possibleNewTargets = target.elligibleTargets(allowReflect=False)
                if len(possibleNewTargets) < 1:
                    return
                caster = target
                target = choice(possibleNewTargets)
            else:
                oldTarget = target
                target = caster
                caster = oldTarget
        self.oncast(caster, target)
        caster.fight.combatLog.append(f'{caster.name} casts {self.name}')


class MultiCastable(Castable):
    def cast(self, caster, targets):
        self.oncast(caster, targets)


def attackFunction(caster):
    caster.attack()


def lightningFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom + caster.level)}d6').roll()
    Damage(amount, DamageTypes.LIGHTNING).deal(target)


def twirlFunction(caster, target):
    for x in range(0, 5):
        caster.attack(caster.getRandomTarget(), 0.25)


def zanmatoFunction(caster, targets):
    for target in caster.elligibleTargets():
        if target != caster:
            caster.attack(target, critGuaranteed=True)


def leechLifeFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom) + caster.level}d4').roll()
    caster.heal(min(amount, target.hp))
    target.harm(amount)


def hasteFunction(caster, target):
    target.applyStatus(Haste)


def multiHasteFunction(caster, targets):
    for target in targets:
        target.applyStatus(Haste)


def dispelFunction(caster, target):
    for status in target.statusEffects.copy():
        if status.dispellable:
            status.remove()


def shieldFunction(caster, target):
    target.applyStatus(Shield)


def magicShieldFunction(caster, target):
    target.applyStatus(MagicalShield)


def reflectFunction(caster, target):
    target.applyStatus(Reflect)


def reviveFunction(caster, target):
    target.revive(0.50)


def resurrectFunction(caster, target):
    target.revive(1)


def resurrectPartyFunction(caster, targets):
    for target in targets:
        target.revive(1)


def regenFunction(caster, target):
    target.applyStatus(Regen)


def cureFunction(caster, target):
    for status in target.statusEffects:
        if status.curable:
            status.remove()


def healFunction(caster, target):
    target.heal(5 * caster.level * (2 + getAttributeMod(caster.wisdom)))


def zombifyingStrikeFunction(caster, target):
    if caster.attack(target):
        target.applyStatus(Zombified, 0.75, 20)


def petrifyingStrikeFunction(caster, target):
    if caster.attack(target):
        target.applyStatus(Petrified, 0.75, 20)


def blindingStrikeFunction(caster, target):
    if caster.attack(target):
        target.applyStatus(Blind, 0.75, 20)


def silencingStrikeFunction(caster, target):
    if caster.attack(target):
        target.applyStatus(Silenced, 0.75, 20)


def stunningStrikeFunction(caster, target):
    if caster.attack(target):
        target.applyStatus(Stunned, 0.75, 20, 4)


magic = Ability(
    name='Magic',
    desc='Dig deeper into all kinds of wizardry yet unknown to you...',
    dependents=[
        blackMagic := Ability(
            name='Black Magic',
            desc='Black',
            dependents=[
                lightning := Castable(
                    name='Lightning',
                    desc='Through controll of the elements, you are able to attack other entities by shooting lightning out of your fingertips. The damage of this spell is determined by rolling a number of d6 (1-6 damage each) equivalent to your wisdom mod+level.',
                    oncast=lightningFunction,
                    repellable=True,
                    castableIfSilenced=False,
                    mpCost=50,
                    dependents=[]
                ),
                drainLife := Castable(
                    name='Drain Life',
                    desc="The use of blood magic allows you to fuel some of the life essence of others back into you. The damage of this spell is determined by rolling a number of d4 (1-4 damage each) equivalent to your wisdom mod+level, which is then added to your HP.",
                    oncast=leechLifeFunction,
                    repellable=True,
                    castableIfSilenced=False,
                    mpCost=70,
                    dependents=[]
                ),
            ]
        ),
        whiteMagic := Ability(
            name='White Magic',
            desc='White Magic',
            dependents=[
                heal := Castable(
                    name='Heal',
                    desc='',
                    oncast=healFunction,
                    mpCost=40,
                    usedOn=UsedOn.FRIENDLY,
                    repellable=True,
                    castableIfSilenced=False,
                    dependents=[
                        cure := Castable(
                            name='Cure',
                            mpCost=30,
                            desc='Removes all negative Effects.',
                            oncast=cureFunction,
                            usedOn=UsedOn.FRIENDLY,
                            repellable=True,
                            castableIfSilenced=False,
                            dependents=[

                            ]
                        ),
                        regen := Castable(
                            name='Regen',
                            mpCost=50,
                            desc='The target gains a constant portion of HP every tick.',
                            oncast=regenFunction,
                            usedOn=UsedOn.FRIENDLY,
                            repellable=True,
                            castableIfSilenced=False,
                            dependents=[

                            ]
                        ),
                        revive := Castable(
                            name='Revive',
                            desc='Revives a dead target and heals it up to 50% HP.',
                            oncast=reviveFunction,
                            usedOn=UsedOn.DEAD,
                            repellable=True,
                            castableIfSilenced=False,
                            mpCost=70,
                            dependents=[
                                resurrect := Castable(
                                    name='Resurrect',
                                    desc='Resurrects target from the dead and heals it up to full HP.',
                                    oncast=resurrectFunction,
                                    mpCost=100,
                                    castableIfSilenced=False,
                                    usedOn=UsedOn.DEAD,
                                    repellable=True,
                                    dependents=[
                                        resurrectParty := MultiCastable(
                                            name='Resurrect Party',
                                            desc='Resurrects multiple targets to full HP.',
                                            oncast=resurrectPartyFunction,
                                            mpCost=200,
                                            usedOn=UsedOn.DEAD,
                                            castableIfSilenced=False,
                                            repellable=True,
                                            dependents=[

                                            ]
                                        )
                                    ]
                                )
                            ]
                        )

                    ]
                ),
                dispel := Castable(
                    name='Dispel',
                    desc='Breaks all spells currently active on the target.',
                    mpCost=50,
                    oncast=dispelFunction,
                    castableIfSilenced=False,
                    dependents=[
                        shield := Castable(
                            name='Shield',
                            desc='Applies 50% resistance against all physical damage.',
                            mpCost=60,
                            oncast=shieldFunction,
                            usedOn=UsedOn.FRIENDLY,
                            castableIfSilenced=False,
                            repellable=True,
                            dependents=[

                            ]
                        ),
                        magicShield := Castable(
                            name='Magic Shield',
                            desc='Applies 50% resistance against all magical damage',
                            mpCost=60,
                            oncast=magicShieldFunction,
                            usedOn=UsedOn.FRIENDLY,
                            castableIfSilenced=False,
                            repellable=True,
                            dependents=[

                            ]
                        ),
                        reflect := Castable(
                            name='Reflect',
                            desc='Applies the reflect buff to a target. This makes any magical spell execept dispel or reflect that is cast on the target be repelled back to its original caster. If the original caster also has reflect, it is given a random target on the casters side without reflect.',
                            mpCost=60,
                            oncast=reflectFunction,
                            castableIfSilenced=False,
                            usedOn=UsedOn.FRIENDLY,
                            dependents=[

                            ]
                        )
                    ]
                ),
                haste := Castable(
                    name='Haste',
                    desc='',
                    mpCost=40,
                    oncast=hasteFunction,
                    castableIfSilenced=False,
                    usedOn=UsedOn.FRIENDLY,
                    repellable=True,
                    dependents=[
                        multiHaste := MultiCastable(
                            name='Multi Haste',
                            desc='',
                            mpCost=60,
                            castableIfSilenced=False,
                            oncast=multiHasteFunction,
                            usedOn=UsedOn.FRIENDLY,
                            repellable=True,
                            dependents=[

                            ]
                        )
                    ]
                )

            ]
        )

    ]
)

armedCombat = Ability(
    name='Armed Combat',
    desc='Fighting with a weapon may be a bit more effective than just hitting, biting, and kicking...',
    dependents=[
        swordFighting1 := Skill(
            name='Sword Fighting I',
            desc='Sword fighting is one of the best forms of fighting, at least when it comes to pure damage output. Cutting up someone not only inflicts a lot of direct damage, but also causes the target to bleed. +1 Attack on Sword',
            properties=[WeaponProficiencyProperty(1, Sword)],
            dependents=[
                swordFighting2 := Skill(
                    name='Sword Fighting II',
                    desc='Your recent advances in sword fighting have given you an additional +1 attack on swords',
                    properties=[WeaponProficiencyProperty(1, Sword)],
                    dependents=[
                        swordFighting3 := Skill(
                            name='Sword Fighting III',
                            desc='Your Training has paid off as you get an additional +1 attack on swords',
                            properties=[WeaponProficiencyProperty(1, Sword)],
                            dependents=[
                                swordFighting4 := Skill(
                                    name='Sword Fighting IV',
                                    desc='You have truly mastered sword fighting to perfection. +2 attack on swords.',
                                    properties=[WeaponProficiencyProperty(2, Sword)],
                                    dependents=[
                                        zanmato := MultiCastable(
                                            name='Zanmato (120 MP)',
                                            desc='A masterful sword technique that attacks all enemies at once and lands a guaranteed crit on each.',
                                            oncast=zanmatoFunction,
                                            dependents=[

                                            ],
                                            mpCost=120,
                                        )
                                    ]
                                )
                            ]
                        ),
                        twirl := MultiCastable(
                            name='Twirl (60 MP)',
                            desc='You swing around with deadly momentum attacking 5 times, dealing 25% weapon damage each to a random target.',
                            mpCost=60,
                            dependents=[],
                            oncast=twirlFunction,
                        ),
                    ]
                ),
            ]
        ),
        duelWielding1 := Skill(
            name='Dual Wielding I',
            desc='This feat balances out your dual wielding penalty from -6/-10 to -6/-6.',
            properties=[DuelWieldingModifierProperty(0, 4)],
            dependents=[
                duelWielding2 := Skill(
                    name='Dual Wielding II',
                    desc='Your dual wield penalty is reduced by 2/2, to -4/-4.',
                    properties=[DuelWieldingModifierProperty(2, 2)],
                    dependents=[
                        duelWielding3 := Skill(
                            name='Dual Wielding III',
                            desc='Your dual wield penalty is reduced again by 2/2, to -2/-2.',
                            properties=[DuelWieldingModifierProperty(2, 2)],
                            dependents=[
                                duelWielding4 := Skill(
                                    name='Dual Wielding IV',
                                    desc='You can wield two weapons at once without penalty.',
                                    properties=[DuelWieldingModifierProperty(2, 2)],
                                    dependents=[

                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        stunningStrike := Castable(
            name='Stunning Strike',
            desc='An attack that has a 75% chance of stunning the target for 4s (DC 12)',
            mpCost=30,
            oncast=stunningStrikeFunction,
            dependents=[
                blindingStrike := Castable(
                    name='Blinding Strike',
                    desc='An attack that has a 75% chance of blinding the target (DC 12)',
                    mpCost=40,
                    oncast=blindingStrikeFunction,
                    dependents=[
                        petrifyingStrike := Castable(
                            name='Petrifying Strike',
                            desc='An attack that has a 75% chance of petrifying the target (DC 12)',
                            mpCost=60,
                            oncast=petrifyingStrikeFunction,
                            dependents=[]
                        )
                    ]
                ),
                silencingStrike := Castable(
                    name='Silencing Strike',
                    desc='An attack that has a 75% chance of silencing the target (DC 12)',
                    mpCost=40,
                    oncast=silencingStrikeFunction,
                    dependents=[
                        zombifyingStrike := Castable(
                            name='Zombifying Strike',
                            desc='An attack that has a 75% chance of zombifying the target (DC 12)',
                            mpCost=60,
                            oncast=zombifyingStrikeFunction,
                            dependents=[]
                        )
                    ]
                )
            ],
        ),

    ]
)

unarmedCombat = Ability(
    name='Unarmed Combat',
    desc='Who needs weapons anyway?',
    dependents=[]
)

SkilltreeRoot = Ability(
    name='...',
    desc='Your studies commence...',
    dependents=[magic, armedCombat, unarmedCombat]
)
