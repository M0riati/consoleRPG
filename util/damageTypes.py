import enum


class DamageTypes(enum.Enum):
    ACID = 0
    BLUDGEONING = 1
    COLD = 2
    FIRE = 3
    LIGHTNING = 4
    PIERCING = 5
    POISON = 6
    SLASHING = 7
    SOUND = 8
    MAGICAL = 9
    UNSTOPPABLE = 10


halvedByShield = [DamageTypes.ACID, DamageTypes.BLUDGEONING, DamageTypes.PIERCING, DamageTypes.SLASHING,
                  DamageTypes.SOUND]
halvedByMagicShield = [DamageTypes.COLD, DamageTypes.LIGHTNING, DamageTypes.FIRE, DamageTypes.MAGICAL]
