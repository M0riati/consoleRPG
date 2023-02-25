import enum

from ability import MultiCastable
from interface import *
from status import Silenced, HPConversion
from util.usedOn import UsedOn


class CommandPanelState(enum.Enum):
    HIDDEN = 0
    MAIN = 1
    ITEM = 2
    ABILITY = 3


class TargetSelectionMode(enum.Enum):
    OFF = 0
    SINGLE = 1
    MULTI = 2


class FightScene(Scene):

    def onSkip(self):
        self.fight.awaitingPlayerInput = False

    @property
    def commandPanelState(self):
        return self._commandPanelState

    @commandPanelState.setter
    def commandPanelState(self, state):
        self._commandPanelState = state
        self.hideAllCommandPanelButtons()
        if state == CommandPanelState.HIDDEN:
            pass
        elif state == CommandPanelState.MAIN:
            self.attackButton.hidden = False
            self.itemsButton.hidden = False
            self.abilitiesButton.hidden = False
            self.skipTurnButton.hidden = False
        elif state == CommandPanelState.ABILITY:
            self.abilitiesWidget.hidden = False
            self.cancelButton.hidden = False
        elif state == CommandPanelState.ITEM:
            self.itemsWidget.hidden = False
            self.cancelButton.hidden = False

    @property
    def targetSelectionMode(self):
        return self._targetSelectionMode

    def setTargetSelectionMode(self, mode, func=None, autoTarget=UsedOn.HOSTILE):
        self.currentSelectionUsedOn = autoTarget
        if mode == TargetSelectionMode.OFF:
            self.setCommandPanelState(CommandPanelState.HIDDEN)
            self.onTargetSelected(self.target if self.targetSelectionMode == TargetSelectionMode.SINGLE else (
                self.fight.enemies if self.multiCursorSelectingEnemies else self.fight.party))
            self.singleCursor.hidden = True
            self.multiCursor.hidden = True
            self.target = 0
        elif mode == TargetSelectionMode.SINGLE:
            self.onTargetSelected = func
            self.singleCursor.hidden = False
            if autoTarget == UsedOn.HOSTILE:
                self.target = len(self.fight.party)
            elif autoTarget == UsedOn.FRIENDLY:
                self.target = self.fight.participants.index(self.fight.currentTurn)
            elif autoTarget.DEAD:
                self.target = self.fight.deadParty[0] if len(self.fight.deadParty) > 0 else len(self.fight.party)
        elif mode == TargetSelectionMode.MULTI:
            self.onTargetSelected = func
            self.multiCursor.hidden = False
            self.multiCursorSelectingEnemies = autoTarget == UsedOn.HOSTILE
        self._targetSelectionMode = mode

    def hideAllCommandPanelButtons(self):
        self.attackButton.hidden = True
        self.itemsButton.hidden = True
        self.abilitiesButton.hidden = True
        self.abilitiesWidget.hidden = True
        self.itemsWidget.hidden = True
        self.skipTurnButton.hidden = True
        self.cancelButton.hidden = True
        self.singleCursor.hidden = True
        self.multiCursor.hidden = True

    def consumeItem(self, i, target):
        self.fight.participants[target].consume(self.fight.currentTurn.inventory.consumables[i])
        self.setCommandPanelState(CommandPanelState.HIDDEN)
        self.fight.awaitingPlayerInput = False

    def onItemSelect(self, i):
        self.setTargetSelectionMode(TargetSelectionMode.SINGLE, func=lambda target: self.consumeItem(i, target),
                                    autoTarget=self.fight.currentTurn.inventory.consumables[i].usedOn)

    def onAttack(self, target):
        self.fight.currentTurn.attack(self.fight.participants[target])
        self.fight.awaitingPlayerInput = False

    def onCastSpell(self, target, spell):
        if self.fight.currentTurn.canUseSpell(spell):
            self.fight.currentTurn.modifyMP(-spell.mpCost)
            spell.cast(self.fight.currentTurn, self.fight.participants[target])
            self.fight.awaitingPlayerInput = False
            self.singleCursor.hidden = True

    def onCastMultiSpell(self, enemies, spell):
        if self.fight.currentTurn.canUseSpell(spell):
            self.fight.currentTurn.modifyMP(-spell.mpCost)
            spell.cast(self.fight.currentTurn, self.fight.enemies if enemies else self.fight.party)
            self.fight.awaitingPlayerInput = False
            self.multiCursor.hidden = True

    def selectSpellTarget(self, i):
        spell = self.fight.currentTurn.castableSpells[i]
        if self.fight.currentTurn.canUseSpell(spell) and not (
                not spell.castableIfSilenced and self.fight.currentTurn.hasStatusOfType(Silenced)):
            if isinstance(spell, MultiCastable):
                self.setTargetSelectionMode(TargetSelectionMode.MULTI,
                                            lambda targets: self.onCastMultiSpell(self.multiCursorSelectingEnemies,
                                                                                  spell), autoTarget=spell.usedOn)
            else:
                self.setTargetSelectionMode(TargetSelectionMode.SINGLE, lambda target: self.onCastSpell(target, spell),
                                            autoTarget=spell.usedOn)

    def singleCursorCoords(self):
        numberOfPCs = len(self.fight.party)
        if self.target - numberOfPCs < 0:
            return 0, 6 * self.target
        else:
            return 78, 6 * (self.target - numberOfPCs)

    def multiCursorCoords(self):
        return (78, 0) if self.multiCursorSelectingEnemies else (0, 0)

    def setCommandPanelState(self, state):
        self.commandPanelState = state

    def multiCursorSpriteGenerator(self):
        return (['>'] + [''] * 5) * (
            len(self.fight.enemies) if self.multiCursorSelectingEnemies else len(self.fight.party))

    def __init__(self, fight):
        super().__init__()
        self.fight = fight
        self.target = 0
        self.onTargetSelected = None
        self.currentSelectionUsedOn = None
        self._targetSelectionMode = None
        self.attackButton = Button(['[Attack]'], 50, 0,
                                   onclick=lambda: self.setTargetSelectionMode(TargetSelectionMode.SINGLE,
                                                                               lambda target: self.onAttack(target)))
        self.itemsButton = Button(['[Items]'], 50, 1, onclick=lambda: self.setCommandPanelState(CommandPanelState.ITEM))
        self.abilitiesButton = Button(['[Abilities]'], 50, 2,
                                      onclick=lambda: self.setCommandPanelState(CommandPanelState.ABILITY))
        self.skipTurnButton = Button(['[Skip Turn]'], 50, 3, onclick=lambda: self.onSkip())
        self.cancelButton = Button(['[Cancel]'], 50, 6,
                                   onclick=lambda: self.setCommandPanelState(CommandPanelState.MAIN))
        self._commandPanelState = CommandPanelState.HIDDEN
        self.itemsWidget = ListWidget([], 50, 0, 5, listProperty='self.fight.currentTurn.inventory.consumables',
                                      onElementSelected=lambda i: self.onItemSelect(i))
        self.abilitiesWidget = ListWidget([], 50, 0, 5, listProperty='self.fight.currentTurn.castableSpells',
                                          onElementSelected=lambda i: self.selectSpellTarget(i),
                                          coloring=lambda e: 0 if e.mpCost >= self.fight.currentTurn.mp else 7)
        self.singleCursor = Sprite(['>'], 48, 0, positionFunction=self.singleCursorCoords)
        self.multiCursor = Sprite([], 48, 0, positionFunction=self.multiCursorCoords,
                                  spriteGeneratorFunction=self.multiCursorSpriteGenerator)
        self.multiCursor.hidden = True
        self.multiCursorSelectingEnemies = True
        self.singleCursor.hidden = True
        self.hideAllCommandPanelButtons()
        self.sprites = [
            Sprite([''], 4, 0, color=Screen.COLOUR_BLUE, spriteGeneratorFunction=lambda: self.partyInfo),
            Sprite([''], 80, 0, color=Screen.COLOUR_RED, spriteGeneratorFunction=lambda: self.enemyInfo),
            ListWidget([''], 0, 25, 4, width=10000, listProperty='self.fight.combatLog', followTail=True),
            self.attackButton,
            self.itemsButton,
            self.abilitiesButton,
            self.abilitiesWidget,
            self.itemsWidget,
            self.skipTurnButton,
            self.cancelButton,
            self.singleCursor,
            self.multiCursor
        ]
        self.musicPath = 'assets/audio/music/newWorld.ogg'

    @property
    def enemyInfo(self):
        enemyInfos = [enemy.getBattleCharacterInfo(turn=enemy == self.fight.currentTurn) for enemy in
                      self.fight.enemies]
        result = []
        for enemyInfo in enemyInfos:
            for line in enemyInfo:
                result.append(line)
            result.append('')
        return result

    @property
    def partyInfo(self):
        pcInfos = [pc.getBattleCharacterInfo(turn=pc == self.fight.currentTurn) for pc in self.fight.party]
        result = []
        for pcInfo in pcInfos:
            for line in pcInfo:
                result.append(line)
            result.append('')
        return result

    def update(self):
        event = self.canvas.event
        if isinstance(event, KeyboardEvent) and self._targetSelectionMode != TargetSelectionMode.OFF:
            if event.key_code in (11, 13):
                if self.targetSelectionMode is TargetSelectionMode.SINGLE:
                    if not self.fight.participants[self.target].dead or (
                            self.fight.participants[self.target].dead and self.currentSelectionUsedOn == UsedOn.DEAD):
                        self.setTargetSelectionMode(TargetSelectionMode.OFF)
                else:
                    self.setTargetSelectionMode(TargetSelectionMode.OFF)
            elif event.key_code == self.canvas.screen.KEY_UP and self.targetSelectionMode == TargetSelectionMode.SINGLE:
                self.target -= 1
                if self.target < 0:
                    self.target = len(self.fight.participants) - 1
            elif event.key_code == self.canvas.screen.KEY_DOWN and self.targetSelectionMode == TargetSelectionMode.SINGLE:
                self.target += 1
                if self.target > len(self.fight.participants) - 1:
                    self.target = 0
            elif event.key_code == self.canvas.screen.KEY_LEFT:
                if self.targetSelectionMode == TargetSelectionMode.SINGLE:
                    if self.target >= len(self.fight.party):
                        self.target -= len(self.fight.party)
                else:
                    self.multiCursorSelectingEnemies = False

            elif event.key_code == self.canvas.screen.KEY_RIGHT:
                if self.targetSelectionMode == TargetSelectionMode.SINGLE:
                    if self.target < len(self.fight.party):
                        self.target += len(self.fight.party)
                else:
                    self.multiCursorSelectingEnemies = True
        if not self.fight.awaitingPlayerInput:
            self.commandPanelState = CommandPanelState.HIDDEN
        elif self.commandPanelState == CommandPanelState.HIDDEN:
            self.commandPanelState = CommandPanelState.MAIN
        if len(self.fight.aliveParty) == 0 or len(self.fight.aliveEnemies) == 0:
            self.canvas.stop()
        self.fight.update(self.canvas.delta)
