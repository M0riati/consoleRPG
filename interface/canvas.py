from time import *

import pyogg
import simpleaudio as sa
from asciimatics.event import *

from interface import *
from util import context


class Canvas:

    def __init__(self, keyboardInputHandler=lambda _: eval('pass'), onnothover=lambda: None):
        self.screen = None
        self.sprites = []
        self.scene = None
        self.mouseX = 0
        self.mouseY = 0
        self.canvasWrapper = None
        self.mouseScroll = 0
        self.leftClick = False
        self.rightClick = False
        self.event = None
        self.context = context.Context(locals(), globals())
        self.keyboardInputHandler = keyboardInputHandler
        self.running = True
        self.onnothover = onnothover
        self.isHovering = False
        self.t = time()
        self.lastT = time()
        self.delta = 0
        self.musicPlayObject = None

    def loadScene(self, scene_):
        self.sprites = []
        self.scene = scene_
        self.context = scene_.context
        self.onnothover = scene_.onnothover
        self.keyboardInputHandler = scene_.keyboardInput
        scene_.canvas = self
        for sprite_ in scene_.sprites:
            self.add(sprite_)

    def stop(self):
        self.running = False
        if self.canvasWrapper is not None:
            self.canvasWrapper.running = False
        if self.scene.musicPath is not None:
            self.musicPlayObject.stop()

    def drawSprites(self):
        self.isHovering = False
        for sprite_ in self.sprites:
            if not sprite_.hidden:
                i = 0
                sprite_.update()
                for line in sprite_.sprite:
                    if line != '':
                        from interface import ColorMappedSprite
                        from interface.listWidget import ListWidget
                        if isinstance(sprite_, ColorMappedSprite):
                            self.screen.paint(self.context.eval(f"""f'''{line}'''"""), sprite_.x, sprite_.y + i,
                                              colour_map=sprite_.colormap[i])
                        elif isinstance(sprite_, ListWidget) and line.lstrip() != '↓':
                            j = i + sprite_.i
                            colour_map = [(sprite_.coloring(sprite_.list[j]) if j < len(sprite_.list) else 7, 0,
                                           0)] * len(
                                sprite_.sprite[i])
                            if sprite_.sprite[i][-1] in ['↑', '↓']:
                                colour_map[-1] = (7, 0, 0)
                            self.screen.paint(self.context.eval(f"""f'''{line}'''"""), sprite_.x, sprite_.y + i,
                                              colour_map=colour_map)
                        else:
                            if isinstance(line, tuple) or isinstance(line, list):
                                self.screen.print_at(self.context.eval(f"""f'''{line[0]}'''"""), sprite_.x,
                                                     sprite_.y + i,
                                                     colour=line[1])
                            else:
                                self.screen.print_at(self.context.eval(f"""f'''{line}'''"""), sprite_.x, sprite_.y + i,
                                                     colour=sprite_.color)
                    i += 1
        if not self.isHovering:
            self.onnothover()

    def add(self, *sprites):
        for sprite_ in sprites:
            sprite_.canvas = self
            sprite_.onAdd()
            self.sprites.append(sprite_)

    def start(self, screen: Screen):
        self.screen = screen
        if self.scene.musicPath is not None and self.musicPlayObject is None:
            vorbisFile = pyogg.VorbisFile(self.scene.musicPath)
            self.musicPlayObject = sa.play_buffer(vorbisFile.buffer, vorbisFile.channels, 2, vorbisFile.frequency)
        while self.running:
            self.t = time()
            self.delta = self.t - self.lastT
            self.scene.update()
            self.event = self.screen.get_event()
            if isinstance(self.event, MouseEvent):
                self.mouseX = self.event.x
                self.mouseY = self.event.y
                self.leftClick = self.event.buttons == self.event.LEFT_CLICK
                self.rightClick = self.event.buttons == self.event.RIGHT_CLICK
            elif isinstance(self.event, KeyboardEvent):
                self.keyboardInputHandler(self.event)
            self.drawSprites()

            self.screen.refresh()
            if self.screen.has_resized():
                Screen.wrapper(self.start)
                return
            else:
                self.screen.clear_buffer(7, 1, 0)
            self.lastT = self.t


class CanvasWrapper:
    def __init__(self, canvas):
        self.canvas = canvas
        self.running = True
        self.canvas.canvasWrapper = self

    def mainLoop(self):
        while self.running:
            Screen.wrapper(self.canvas.start)
            self.canvas.screen.close()
