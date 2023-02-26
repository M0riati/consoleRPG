from random import choice

from items import Sword
from status import *
from util import *
from util.usedOn import UsedOn


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
                 castableIfSilenced=True, castableOnSelf=True):
        super().__init__(name, desc, dependents)
        self.dependents = dependents
        self.mpCost = mpCost
        self.oncast = oncast
        self.hpCost = hpCost
        self.usedOn = usedOn
        self.castableOnSelf = castableOnSelf
        self.repellable = repellable
        self.castableIfSilenced = castableIfSilenced

    def __repr__(self):
        return f'{self.name}'

    def reprWithCost(self, conversion=False):
        if self.mpCost == 0 and self.hpCost == 0:
            return self.__repr__()
        if not conversion:
            if self.mpCost > 0 and self.hpCost > 0:
                return f'{self.name} ({self.mpCost}MP, {self.hpCost}HP)'
            elif self.mpCost > 0:
                return f'{self.name} ({self.mpCost}MP)'
            elif self.hpCost > 0:
                return f'{self.name} ({self.hpCost}HP)'
        return f'{self.name} ({self.mpCost//2}MP, {self.hpCost+self.mpCost//4}HP)'


    def cast(self, caster, target):
        oldCaster = caster
        oldTarget = target
        reflected = self.repellable and target.hasStatusOfType(Reflect)
        if reflected:
            if target.hasStatusOfType(Reflect):
                possibleNewTargets = target.elligibleTargets(allowReflect=False)
                if len(possibleNewTargets) < 1:
                    return
                caster = oldTarget
                target = choice(possibleNewTargets)
            else:
                target = oldCaster
                caster = oldTarget
        caster.fight.combatLog.append(f'{oldCaster.name} casts {self.name} on {oldTarget.name if oldTarget != oldCaster else "himself"}{f", but the spell is reflected, hitting {target.name}" if reflected else """"""}.')
        self.oncast(caster, target)


class MultiCastable(Castable):
    def cast(self, caster, targets):
        self.oncast(caster, targets)

class SelfCastable(Castable):
    def cast(self, caster, target=None):
        self.oncast(caster)

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


def drainHPFunction(caster, target):
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


def burnFunction(caster, target):
    target.applyStatus(Burning, 1, 20, 8)

def incinerateFunction(caster, target):
    target.applyStatus(Burning, 1, 25, 16)
    amount = Dice('1d10').roll()
    Damage(amount, DamageTypes.FIRE).deal(target)

def fireballFunction(caster, target):
    target.applyStatus(Burning, 0.6, 20, 4)
    amount = Dice(f'{getAttributeMod(caster.wisdom) + caster.level}d4').roll()
    Damage(amount, DamageTypes.FIRE).deal(target)
def firewallFunction(caster, targets):
    for target in targets:
        target.applyStatus(Burning, 0.6, 20, 4)
        amount = Dice(f'{getAttributeMod(caster.wisdom) + caster.level}d4').roll()
        Damage(amount, DamageTypes.FIRE).deal(target)

def explosionFunction(caster, target):
    target.applyStatus(Burning, 1, 20, 4)
    amount = Dice(f'{getAttributeMod(caster.wisdom) + caster.level}d6').roll()
    Damage(amount, DamageTypes.FIRE).deal(target)

def meteorFunction(caster, target):
    target.applyStatus(Burning, 1, 25, 4)
    amount = Dice(f'{caster.level+getAttributeMod(caster.wisdom)}d12').roll()
    Damage(amount, DamageTypes.FIRE).deal(target)

def waveFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom)+caster.level}d4').roll()
    Damage(amount, DamageTypes.WATER).deal(target)

def waterBeamFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom)+caster.level}d4').roll()
    Damage(amount, DamageTypes.WATER).deal(target)

def tsunamiFunction(caster, targets):
    for target in targets:
        amount = Dice(f'{getAttributeMod(caster.wisdom) + caster.level}d4').roll()
        Damage(amount, DamageTypes.WATER).deal(target)

def vortexFunction(caster, target):
    target.applyStatus(Vortex, 1, 20, 5)

def geyserFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom)+caster.level}d6').roll()
    Damage(amount*0.66, DamageTypes.WATER).deal(target)
    Damage(amount*0.33, DamageTypes.FIRE).deal(target)

def gustFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom)}d4').roll()
    Damage(amount, DamageTypes.AIR).deal(target)

def tornadoFunction(caster, target):
    target.applyStatus(Tornado, 1, 20, 5)

def hurricaneFunction(caster, targets):
    for target in targets:
        target.applyStatus(Tornado, 0.8, 25, 8)

def freezeFunction(caster, target):
    target.applyStatus(Frozen, 1, 25, 16)
    amount = Dice(f'{getAttributeMod(caster.wisdom)}d6').roll()
    Damage(amount, DamageTypes.COLD).deal(target)

def icicleBarrageFunction(caster, target):
    times = Dice(f'{getAttributeMod(caster.wisdom)+caster.level}d10').roll()
    caster.fight.combatLog.append(f'Hitting {times}x')
    for x in range(0, times):
        Damage(1, DamageTypes.COLD).deal(target, log=False)

def hailstormFunction(caster, targets):
    times = Dice(f'{getAttributeMod(caster.wisdom)+caster.level}d4').roll()
    caster.fight.combatLog.append(f'Hitting {times}x')
    for x in range(0, times):
        Damage(4, DamageTypes.COLD).deal(choice(targets), log=False)

def cometFunction(caster, target):
    amount = Dice(f'{caster.level+getAttributeMod(caster.wisdom)}d10').roll()
    Damage(amount, DamageTypes.COLD).deal(target)

def shockFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom) + caster.level}d4').roll()
    target.applyStatus(Stunned, 0.75, 20, 4)
    Damage(amount, DamageTypes.LIGHTNING).deal(target)


def lightningStrikeFunction(caster, target):
    amount = Dice(f'{getAttributeMod(caster.wisdom + caster.level)}d8').roll()
    Damage(amount, DamageTypes.LIGHTNING).deal(target)

def stormFunction(caster, targets):
    for x in range(0, random.randint(3, 5)):
        target = choice(targets)
        amount = Dice(f'{getAttributeMod(caster.wisdom + caster.level)}d6').roll()
        Damage(amount, DamageTypes.LIGHTNING).deal(target)

def shockBarrierFunction(caster, target):
    target.applyStatus(ShockBarrier)

def tapLifeFunction(caster, target):
    target.applyStatus(LifeTapped, caster=caster)

def bloodsplosionFunction(caster, target):
    if target.hpPercentage < abs(Dice('10d10').roll()-20)/100:
        target.hp = 0
    else:
        target.hp *= 0.8

def bloodMarkHPFunction(caster, target):
    target.applyStatus(BloodMarkHP, caster=caster)

def bloodMarkMPFunction(caster, target):
    target.applyStatus(BloodMarkMP, caster=caster)

def toggleHPConversionFunction(caster):
    if caster.hasStatusOfType(HPConversion):
        for status in caster.statusEffects:
            if isinstance(status, HPConversion):
                status.remove()
    else:
        caster.applyStatus(HPConversion)



magic = Ability(
    name='Magic',
    desc='Dig deeper into all kinds of wizardry yet unknown to you...',
    dependents=[
        blackMagic := Ability(
            name='Black Magic',
            desc='',
            dependents=[
                elementalMagic := Ability(
                    name='Elemental Magic',
                    desc='',
                    dependents=[
                        fire := Ability(
                            name='Fire',
                            desc='',
                            dependents=[
                                burn := Castable(
                                    name='Burn',
                                    desc='Causes the target to burn.',
                                    oncast=burnFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=30,
                                    dependents=[
                                        incinerate := Castable(
                                            name='Incinerate',
                                            desc='Deals 1d10 damage and causes the target to burn.',
                                            oncast=incinerateFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=50,
                                            dependents=[
                                                fireball := Castable(
                                                    name='Fireball',
                                                    desc='Attack with a ball of pure fire, dealing 1d4 * (wisdom mod + level) damage and causing the target to burn.',
                                                    oncast=fireballFunction,
                                                    repellable=True,
                                                    castableIfSilenced=False,
                                                    mpCost=60,
                                                    dependents=[
                                                        firewall := MultiCastable(
                                                            name='Firewall',
                                                            desc='Create a wall of fire that effects multiple targets, dealing 1d4 * (wisdom mod + level) damage each and inflicting burn.',
                                                            oncast=firewallFunction,
                                                            castableIfSilenced=False,
                                                            mpCost=80,
                                                            dependents=[

                                                            ]
                                                        ),
                                                        explosion := Castable(
                                                            name='Explosion',
                                                            desc='Set off an explosion near the target that deals 1d6 * (wisdom mod + level) damage to the target and causes it to burn.',
                                                            oncast=explosionFunction,
                                                            repellable=True,
                                                            castableIfSilenced=False,
                                                            mpCost=70,
                                                            dependents=[
                                                                meteor := Castable(
                                                                    name='Meteor',
                                                                    desc='Summon a meteor that deals 1d12 * (wisdom mod + level) fire damage.',
                                                                    oncast=meteorFunction,
                                                                    repellable=True,
                                                                    castableIfSilenced=False,
                                                                    mpCost=100,
                                                                    dependents=[

                                                                    ]
                                                                )
                                                            ]
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        water := Ability(
                            name='Water',
                            desc='',
                            dependents=[
                                wave := Castable(
                                    name='Wave',
                                    desc='Hit one enemy with a wave of water, inflicting 1d4 * (wisdom mod + level) water damage.',
                                    oncast=waveFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=35,
                                    dependents=[
                                        tsunami := MultiCastable(
                                            name='Tsunami',
                                            desc='Hit all enemies with a gigantic wave, inflicting 1d4 * (wisdom mod + level) water damage.',
                                            oncast=tsunamiFunction,
                                            castableIfSilenced=False,
                                            mpCost=85,
                                            dependents=[

                                            ]
                                        ),
                                        vortex := Castable(
                                            name='Vortex',
                                            desc='Trap the target in a vortex, making the target unable to act and dealing a small amount of damage for 5s.',
                                            oncast=vortexFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=80,
                                            dependents=[

                                            ]
                                        ),
                                    ]
                                ),
                                waterBeam := Castable(
                                    name='Water Beam',
                                    desc='Fire a beam of water at the target, dealing 1d4 * (wisdom mod + level)',
                                    oncast=waterBeamFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=50,
                                    dependents=[
                                        geyser := Castable(
                                            name='Geyser',
                                            desc='Deals 1d6 * (wisdom mod + level), 33% of which is converted to fire damage.',
                                            oncast=geyserFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=70,
                                            dependents=[

                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                        air := Ability(
                            name='Air',
                            desc='',
                            dependents=[
                                gust := Castable(
                                    name='Gust',
                                    desc='Summon a small gust of wind, dealing 1d4 * (wisdom mod + level) damage to the target.',
                                    oncast=gustFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=30,
                                    dependents=[
                                        tornado := Castable(
                                            name='Tornado',
                                            desc='Trap the target in a tornado, making the target unable to act and dealing a small amount of damage for 5s.',
                                            oncast=tornadoFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=70,
                                            dependents=[
                                                hurricane := MultiCastable(
                                                    name='Hurricane',
                                                    desc='Trap all targets in a large tornado, making them unable to act and dealing a small amount of damage for 8s.',
                                                    oncast=hurricaneFunction,
                                                    castableIfSilenced=False,
                                                    mpCost=90,
                                                    dependents=[

                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        ice := Ability(
                            name='Ice',
                            desc='',
                            dependents=[
                                freeze := Castable(
                                    name='Freeze',
                                    desc='Freeze a target.',
                                    oncast=freezeFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=50,
                                    dependents=[
                                        IcicleBarrage := Castable(
                                            name='Icicle Barrage',
                                            desc='Fire 1d10 * (wisdom mod + level) icicles, dealing 1 cold damage each.',
                                            oncast=icicleBarrageFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=70,
                                            dependents=[

                                            ]
                                        ),
                                        Hailstorm := MultiCastable(
                                            name='Hailstorm',
                                            desc='Summon a devastating hailstorm that deals 4 cold damage to a random target 1d10 * (wisdom mod + level) times.',
                                            oncast=hailstormFunction,
                                            castableIfSilenced=False,
                                            mpCost=70,
                                            dependents=[
                                                Comet := Castable(
                                                    name='Comet',
                                                    desc='Summon an icy comet that deals 1d10 * (wisdom mod + level) cold damage.',
                                                    oncast=cometFunction,
                                                    repellable=True,
                                                    castableIfSilenced=False,
                                                    mpCost=100,
                                                    dependents=[

                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        electricity := Ability(
                            name='Electricity',
                            desc='',
                            dependents=[
                                lightning := Castable(
                                    name='Lightning',
                                    desc='Through control of the elements, you are able to attack other entities by shooting lightning out of your fingertips. The damage of this spell is determined by rolling a number of d6 (1-6 damage each) equivalent to your wisdom mod+level.',
                                    oncast=lightningFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=50,
                                    dependents=[

                                    ]
                                ),
                                shock := Castable(
                                    name='Shock',
                                    desc='By quickly discharging Electricity at a high voltage, you are able to paralyze the target while effectively dealing 1d4 * (wisdom mod + level) damage.',
                                    oncast=shockFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=50,
                                    dependents=[
                                        lightningStrike := Castable(
                                            name='Lightning Strike',
                                            desc='The target gets struck by lightning and takes 1d8 * (wisdom mod + level) damage.',
                                            oncast=lightningStrikeFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=70,
                                            dependents=[
                                                storm := MultiCastable(
                                                    name='Storm',
                                                    desc='3-5x: A random target gets struck by lightning and takes 1d6 * (wisdom mod + level) damage.',
                                                    oncast=stormFunction,
                                                    repellable=True,
                                                    castableIfSilenced=False,
                                                    mpCost=130,
                                                    dependents=[

                                                    ]
                                                ),
                                            ]
                                        ),
                                        shockBarrier := Castable(
                                            name='Shock barrier',
                                            desc='You engulf your target in a magical barrier that triggers every time an enemy makes a physical attack on them, dealing 1d4 * (wisdom mod + level) to the attacker and paralyzing them.',
                                            oncast=shockBarrierFunction,
                                            repellable=True,
                                            castableIfSilenced=False,
                                            mpCost=70,
                                            dependents=[

                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
                bloodMagic := Ability(
                    name='Blood Magic',
                    desc='Blood magic enables the use of abilities some might consider unnatural (and unethical).',
                    dependents=[
                        drainHP := Castable(
                            name='Drain HP',
                            desc="The use of blood magic allows you to fuel some of the life essence of others back into you. The damage of this spell is determined by rolling a number of d4 (1-4 damage each) equivalent to your wisdom mod+level, which is then added to your HP.",
                            oncast=drainHPFunction,
                            castableOnSelf=False,
                            repellable=True,
                            castableIfSilenced=False,
                            mpCost=60,
                            dependents=[
                                tapLife := Castable(
                                    name='Tap Life',
                                    desc="Even more insidious, this ability allows you to passively funnel some your the target\'s hp in to your own every tick.",
                                    oncast=tapLifeFunction,
                                    castableOnSelf=False,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    mpCost=90,
                                    dependents=[

                                    ]
                                ),
                            ]
                        ),
                        hpConversion := SelfCastable(
                            name='HP Conversion',
                            desc='Being the signature move of the blood mage, with HP conversion enabled, you are able to satisfy 50% of the MP cost of any spell with HP at an exchange rate of 1HP = 2MP.',
                            mpCost=0,
                            oncast=toggleHPConversionFunction,
                            dependents=[
                                bloodMarkHP := Castable(
                                    name='Blood Mark, HP',
                                    desc="Every time the target of this spell takes damage, 30% of that damage are added to your HP.",
                                    oncast=bloodMarkHPFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    castableOnSelf=False,
                                    mpCost=100,
                                    dependents=[

                                    ]
                                ),
                                bloodMarkMP := Castable(
                                    name='Blood Mark, MP',
                                    desc="Every time the target of this spell takes damage, 60% of that damage are added to your MP.",
                                    oncast=bloodMarkMPFunction,
                                    repellable=True,
                                    castableIfSilenced=False,
                                    castableOnSelf=False,
                                    mpCost=100,
                                    dependents=[

                                    ]
                                )
                            ]
                        ),
                        Bloodsplosion := Castable(
                            name='Bloodsplosion',
                            desc="By stirring up the blood in the target\'s bloodstream, you violently cause the target\'s body to explode into a gory mush, inflicting instant death if the target is below |10d10-20|% of their maximum health, otherwise reducing their health by 20%.",
                            oncast=bloodsplosionFunction,
                            repellable=True,
                            castableIfSilenced=False,
                            mpCost=70,
                            dependents=[

                            ]
                        ),

                    ]
                ),
            ]
        ),
        whiteMagic := Ability(
            name='White Magic',
            desc='',
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
                            desc='Applies the reflect buff to a target. This makes any magical spell except dispel or reflect that is cast on the target be repelled back to its original caster. If the original caster also has reflect, it is given a random target on the casters side without reflect.',
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
                    desc='Makes the target gain initiative 2x faster.',
                    mpCost=40,
                    oncast=hasteFunction,
                    castableIfSilenced=False,
                    usedOn=UsedOn.FRIENDLY,
                    repellable=True,
                    dependents=[
                        multiHaste := MultiCastable(
                            name='Multi Haste',
                            desc='Makes all targets gain initiative 2x faster',
                            mpCost=60,
                            castableIfSilenced=False,
                            oncast=multiHasteFunction,
                            usedOn=UsedOn.FRIENDLY,
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
                                            name='Zanmatō (120 MP)',
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

skilltreeRoot = Ability(
    name='...',
    desc='Your studies commence...',
    dependents=[magic, armedCombat, unarmedCombat]
)
