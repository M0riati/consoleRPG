import enum


class DamageTypes(enum.Enum):
    ACID = 0
    BLUDGEONING = 1
    COLD = 2
    FIRE = 3
    WATER = 4
    AIR = 5
    LIGHTNING = 6
    PIERCING = 7
    POISON = 8
    SLASHING = 9
    SOUND = 10
    MAGICAL = 11
    UNSTOPPABLE = 12


halvedByShield = [DamageTypes.ACID, DamageTypes.BLUDGEONING, DamageTypes.PIERCING, DamageTypes.SLASHING,
                  DamageTypes.SOUND]
halvedByMagicShield = [DamageTypes.COLD, DamageTypes.LIGHTNING, DamageTypes.FIRE, DamageTypes.WATER, DamageTypes.AIR, DamageTypes.MAGICAL]
