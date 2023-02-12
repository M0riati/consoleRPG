from asciimatics.screen import Screen


class Sprite:
    def __init__(self, sprite_, x, y, onhover=lambda: None, canvas_=None, color=Screen.COLOUR_WHITE,
                 spriteGeneratorFunction=None, positionFunction=lambda: exec('pass'), hidden=False):
        self.canvas = canvas_
        self.positionFunction = positionFunction
        self.spriteGeneratorFunction = spriteGeneratorFunction if spriteGeneratorFunction is not None else self.dummySpriteGenerator
        self.x = x
        self.y = y
        self.onhover = onhover
        self._sprite = sprite_
        self.color = color
        self.hidden = hidden

    def dummySpriteGenerator(self):
        return self._sprite

    def onAdd(self):
        pass

    def isClicked(self):
        return (
                self.canvas.leftClick and
                self.y <= self.canvas.mouseY <= self.y + len(self.sprite) - 1 and
                self.x <= self.canvas.mouseX <= self.x + len(self.sprite[self.canvas.mouseY - self.y]) - 1
        )

    def isRightClicked(self):
        return (
                self.canvas.rightClick and
                self.y <= self.canvas.mouseY <= self.y + len(self.sprite) - 1 and
                self.x <= self.canvas.mouseX <= self.x + len(self.sprite[self.canvas.mouseY - self.y]) - 1
        )

    def isHovered(self):
        return (
                self.y <= self.canvas.mouseY <= self.y + len(self.sprite) - 1 and
                self.x <= self.canvas.mouseX <= self.x + len(self.sprite[self.canvas.mouseY - self.y]) - 1
        )

    @property
    def sprite(self):
        return self.spriteGeneratorFunction()

    @sprite.setter
    def sprite(self, value):
        self._sprite = value

    def update(self):
        if self.isHovered():
            self.onhover()
            self.canvas.isHovering = True
        if self.positionFunction() is not None:
            self.x = self.positionFunction()[0]
            self.y = self.positionFunction()[1]


class ColorMappedSprite(Sprite):
    def __init__(self, sprite_, x, y, kwargs):
        super().__init__(sprite_, x, y)
        self.colormap = []
        for line in sprite_:
            colormapLine = []
            for char in line:
                if char in kwargs.keys():
                    colormapLine.append((kwargs[char], 0, 0))
                else:
                    colormapLine.append((0, 0, 0))
            self.colormap.append(colormapLine)
