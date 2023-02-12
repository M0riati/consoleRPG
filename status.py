class Status:

    def __init__(self, target, duration=None, caster=None):
        self.target = target
        self.caster = caster
        self.duration = duration
        self.name = ''
        self.curable = False
        self.dispellable = False

    def effect(self, delta):
        if self.duration is not None:
            self.duration -= delta
            if self.duration <= 0:
                self.remove()

    def onApply(self):
        pass

    def remove(self):
        self.target.statusEffects.remove(self)

    def __repr__(self):
        return self.name


class SpeedModifyingStatus(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.speedModifier = None


class Slowed(SpeedModifyingStatus):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.name = 'Slowed'
        self.speedModifier = 0.5
        self.dispellable = True


class Stunned(SpeedModifyingStatus):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.name = 'Stunnd'
        self.speedModifier = 0
        self.curable = True


class Silenced(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.curable = True
        self.name = 'Silenced'


class Zombified(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.curable = True
        self.name = 'Zombified'


class Petrified(SpeedModifyingStatus):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.speedModifier = 0
        self.curable = True
        self.name = 'Petrified'


class Frozen(SpeedModifyingStatus):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.speedModifier = 0
        self.name = 'Frozen'


class Burning(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.name = 'Burning'

    def effect(self, delta):
        self.target.harm(delta * 10)


class Regen(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.dispellable = True
        self.name = 'Regen'

    def effect(self, delta):
        self.target.heal(delta * (1 - self.target.hpPercentage ** 2) * 25)


class Haste(SpeedModifyingStatus):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.speedModifier = 2
        self.dispellable = True
        self.name = 'Haste'


class Reflect(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.name = 'Reflect'
        self.dispellable = True


class Shield(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.name = 'Shield'
        self.dispellable = True


class MagicalShield(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.name = 'Magical Shield'
        self.dispellable = True


class Poisoned(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.curable = True
        self.name = 'Poisoned'

    def effect(self, delta):
        self.target.harm(delta * 5)


class Blind(Status):
    def __init__(self, target, duration=None):
        super().__init__(target, duration)
        self.curable = True
        self.name = 'Blind'


class Bleeding(Status):
    def __init__(self, target, totalDmg, caster=None):
        super().__init__(target, duration=None, caster=caster)
        self.totalDmg = totalDmg
        self.curable = True
        self.name = 'Bleeding'

    def effect(self, delta):
        damage = min(delta * 20, self.totalDmg)
        self.totalDmg -= damage
        self.target.harm(damage)
        if self.totalDmg <= 0:
            self.remove()


class VampiricBleeding(Bleeding):
    def __init__(self, target, totalDmg, caster=None):
        super().__init__(target, totalDmg, caster)
        self.dispellable = True,
        self.name = 'Vampiric Bleeding'

    def effect(self, delta):
        damage = min(delta * 20, self.totalDmg)
        self.totalDmg -= damage
        self.target.harm(damage)
        self.caster.heal(damage)
        if self.totalDmg <= 0:
            self.remove()
