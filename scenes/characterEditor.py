import copy

import namegen
from character import *
from interface import *
from interface.listWidget import ListWidget

descriptions = [
    'The overall physical strength of a character. Your modifier is added after your damage roll.',
    'Determines the toughness and vitality of a character. Your max HP is determined after 10*level*(5+constitution modifier).',
    'Dexterity determines the overall attack speed and reaction time of a character. A higher modifier means higher evasion and accuracy, as well as increased attack speed.',
    'Intelligence is a more versatile attribute that determines how adaptable a character is. A lot of practical abilities have a minimum intelligence requirement or take one\'s intelligence modifier into acount',
    'Wisdom is the ability to control one\'s power. Some abilities require a minimum amount of wisdom to be truly used effectively. A higher modifier increases magical damage as well.'
]


class CharacterEditor(Scene):
    def addSign(self, value):
        return f'+{value}' if value >= 0 else str(value)

    @staticmethod
    def getAttributeMod(attribute):
        mod = attribute // 2 - 5
        return ('+' if mod >= 0 else '') + str(mod)

    def keyboardInput(self, event):
        super().keyboardInput(event)
        assert isinstance(event, KeyboardEvent)
        if event.key_code == Screen.KEY_BACK:
            if len(self.character.name) > 0:
                self.character.name = self.character.name[:-1]
        elif 32 <= event.key_code <= 126:
            self.character.name += chr(event.key_code)

    def setAttributeDesc(self, attr=None):
        if attr is None:
            self.currentAttrDesc = ''
            self.describedWeapon = None
        else:
            self.currentAttrDesc = descriptions[attr]

    def setNameDesc(self):
        self.currentAttrDesc = 'Click here to generate a new name or type in a custom one.'

    def setHealthDesc(self):
        self.currentAttrDesc = 'Your current health followed by your maximum health. If the former decrease to 0, you\'re dead.'

    def setMPDesc(self):
        self.currentAttrDesc = 'Your current MP followed by your maximum MP. MP are used to cast spells.'

    def setLearnableAbilityDesc(self, i):
        if i is None:
            self.currentAttrDesc = ''
        else:
            try:
                self.currentAttrDesc = self.character.availableAbilities[i].desc
            except IndexError:
                self.setAttributeDesc()

    def setLearntAbilityDesc(self, i):
        if i is None:
            self.currentAttrDesc = ''
        else:
            try:
                self.currentAttrDesc = self.character.abilities[i].desc
            except IndexError:
                self.setAttributeDesc()

    def learnAbility(self, i):
        self.character.learn(self.character.availableAbilities[i])

    def unlearnAbility(self, i):
        self.character.unlearn(self.character.abilities[i])

    def randomName(self):
        self.character.name = namegen.generateCharacterName()

    def selectMainHandWeapon(self, i):
        self.character.mainHand = copy.deepcopy(self.availableWeapons[i])

    def selectOffHandWeapon(self, i):
        self.character.offHand = copy.deepcopy(self.availableWeapons[i])

    def setDescribedWeapon(self, weapon_):
        self.describedWeapon = weapon_

    def removeOffHandWeapon(self):
        self.character._offHand = None

    def __init__(self, character):
        super().__init__()
        column1 = 1
        column2 = column1 + 17
        column3 = column2 + 10
        column4 = column3 + 6
        self.character = character
        self.currentAttrDesc = ''
        self.availableWeapons = [Warhammer(), Mace(), MorningStar(), Spear(), Shortsword(), Wakizashi(), Katana(),
                                 ArmingSword(), BastardSword(), Longsword(), Greatsword()]
        self.onnothover = self.setAttributeDesc
        self.musicPath = 'assets/audio/music/neptune.ogg'
        self.weaponDesc = Textbox('{self.describedWeapon.desc if self.describedWeapon is not None else ""}',
                                  column4 + 20, 17, 60, scrolling=False)
        self.describedWeapon = None
        self.sprites = [
            Textbox('{self.currentAttrDesc}', column4 + 15, 3, 60, scrolling=False),
            Button(['Name: {self.character.name+"|"*round((self.canvas.t/0.75)%1)}'], column1, 0,
                   onclick=lambda: self.randomName(), onhover=lambda: self.setNameDesc()),
            Sprite(['=' * (column4 + 4)], 1, 3),
            Sprite(['HP: {self.character.getHealthBar()}'], column1, 1, color=Screen.COLOUR_RED,
                   onhover=lambda: self.setHealthDesc()),
            Sprite(['MP: {self.character.getMPBar()}'], column1, 2, color=Screen.COLOUR_BLUE),
            Sprite(['Strength'], column1, 4, onhover=lambda: self.setAttributeDesc(0)),
            Sprite(['{self.character.baseStrength}   {self.getAttributeMod(self.character.baseStrength)}'], column2, 4),
            Button(['[+]'], column3, 4, lambda: self.character.spendAttributePoint('str')),
            Button(['[-]'], column4, 4, lambda: self.character.reclaimAttributePoint('str')),

            Sprite(['Constitution'], column1, 5, onhover=lambda: self.setAttributeDesc(1)),
            Sprite(['{self.character.baseConstitution}   {self.getAttributeMod(self.character.baseConstitution)}'],
                   column2, 5),
            Button(['[+]'], column3, 5, lambda: self.character.spendAttributePoint('tgh')),
            Button(['[-]'], column4, 5, lambda: self.character.reclaimAttributePoint('tgh')),

            Sprite(['Dexterity'], column1, 6, onhover=lambda: self.setAttributeDesc(2)),
            Sprite(['{self.character.baseDexterity}   {self.getAttributeMod(self.character.baseDexterity)}'], column2,
                   6),
            Button(['[+]'], column3, 6, lambda: self.character.spendAttributePoint('dex')),
            Button(['[-]'], column4, 6, lambda: self.character.reclaimAttributePoint('dex')),

            Sprite(['Intelligence'], column1, 7, onhover=lambda: self.setAttributeDesc(3)),
            Sprite(['{self.character.baseIntelligence}   {self.getAttributeMod(self.character.baseIntelligence)}'],
                   column2, 7),
            Button(['[+]'], column3, 7, lambda: self.character.spendAttributePoint('int')),
            Button(['[-]'], column4, 7, lambda: self.character.reclaimAttributePoint('int')),

            Sprite(['Wisdom'], column1, 8, onhover=lambda: self.setAttributeDesc(4)),
            Sprite(['{self.character.baseWisdom}   {self.getAttributeMod(self.character.baseWisdom)}'], column2, 8),
            Button(['[+]'], column3, 8, lambda: self.character.spendAttributePoint('wis'), lambda: -1),
            Button(['[-]'], column4, 8, lambda: self.character.reclaimAttributePoint('wis')),

            Sprite([('Available Abilities', 1)], column1, 10),
            Sprite([('Learnt Abilities', 1)], column4, 10),

            ListWidget([], column1, 11, 5, listProperty='self.character.availableAbilities',
                       onElementSelected=lambda i: self.learnAbility(i),
                       onElementHovered=lambda i: self.setLearnableAbilityDesc(i)),
            ListWidget([], column4, 11, 5, listProperty='self.character.abilities',
                       onElementSelected=lambda i: self.unlearnAbility(i),
                       onElementHovered=lambda i: self.setLearntAbilityDesc(i),
                       coloring=lambda e: 2 if e in character.justLearnt else 7),
            Sprite(['Available Weapons'], column1, 17, color=1),
            Sprite(['Main Hand'], column4, 17, color=1),
            Sprite(['Off Hand'], column4, 20, color=1),
            ListWidget([], column1, 18, 4, listProperty='self.availableWeapons',
                       onElementSelected=lambda i: self.selectMainHandWeapon(i),
                       onElementRightClicked=lambda i: self.selectOffHandWeapon(i),
                       onElementHovered=lambda i: self.setDescribedWeapon(self.availableWeapons[i])),
            Sprite([
                       '{self.character.mainHand} {"("+self.addSign(self.character.mainHand.attackMod)+")" if self.character.mainHand is not None else ""}'],
                   column4, 18, onhover=lambda: self.setDescribedWeapon(self.character.mainHand)),
            Button([
                       '{self.character.offHand} {"("+self.addSign(self.character.offHand.attackMod)+")" if self.character.offHand is not None else ""}'],
                   column4, 21, onhover=lambda: self.setDescribedWeapon(self.character.offHand),
                   onclick=lambda: self.removeOffHandWeapon()),
            self.weaponDesc,
            Sprite([], column4 + 20, 18, positionFunction=lambda: (column4 + 20, 18 + len(self.weaponDesc.sprite)),
                   spriteGeneratorFunction=lambda: self.describedWeapon.propertyDesc if self.describedWeapon is not None else [
                       '']),
            Sprite(['Skill Points remaining: {self.character.skillPointsRemaining}'], column1, 26),

            Sprite(['Attribute Points remaining: {self.character.attributePointsRemaining}'], column1, 27),
            Button(['[Accept]'], column4, 27, lambda: self.canvas.stop())
        ]
