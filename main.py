from fight import *
from items.phoenixDown import PhoenixDown
from nonPlayerCharacter import randomNPC
from playerCharacter import PlayerCharacter
from scenes import *
from scenes.victory import Victory
from scenes.youDied import YouDied

pc = PlayerCharacter('Typski', lvl=6)
pc.inventory.addItem(Potion(5))
pc.inventory.addItem(PhoenixDown(3))
canvas = Canvas()
canvas.loadScene(CharacterEditor(pc))
Screen.wrapper(canvas.start)
enemies = [randomNPC(3, True) for _ in range(0, 4)]
canvas = Canvas()
fightScene = FightScene(Fight([pc], enemies))
canvas.loadScene(fightScene)
Screen.wrapper(canvas.start)

canvas = Canvas()

if len(fightScene.fight.aliveEnemies) > 0:
    canvas.loadScene(YouDied())
else:
    canvas.loadScene(Victory())

Screen.wrapper(canvas.start)
