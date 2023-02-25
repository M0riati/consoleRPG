from interface.sprite import Sprite


class ListWidget(Sprite):
    def __init__(self, list_, x, y, height=5, listProperty=None, onElementSelected=lambda i: None, positionFunction=lambda: None,
                 onElementRightClicked=lambda i: None,
                 onElementHovered=lambda i: None, width=25, coloring=lambda e: 7, reprFunction=lambda e: str(e), followTail=False):
        if listProperty is None:
            listProperty = ''
        self.onElementHovered = onElementHovered
        self.onElementSelected = onElementSelected
        self.onElementRightClicked = onElementRightClicked
        self.reprFunction = reprFunction
        self._list = list_
        self.height = height
        self.width = width
        self.followTail = followTail
        self.i = 0
        self.coloring = coloring
        self.listProperty = listProperty
        super().__init__('', x, y, positionFunction=positionFunction)

    def update(self):
        super().update()
        if self.isClicked() or self.isRightClicked():
            if len(self.list) > self.height and self.canvas.mouseX == self.x + self.width and self.canvas.mouseY in (
                    self.y, self.y + len(
                        self.sprite) - 1) and not self.isRightClicked():
                if self.canvas.mouseY == self.y:
                    self.i -= 1 if self.i > 0 else 0
                elif self.canvas.mouseY == self.y + self.height - 1:
                    self.i += 1 if self.i < len(self.list) - self.height else 0
            else:
                i = (self.canvas.mouseY - self.y) + self.i
                if self.canvas.rightClick:
                    self.onElementRightClicked(i)
                if self.canvas.leftClick:
                    self.onElementSelected(i)
            self.canvas.rightClick = False
            self.canvas.leftClick = False
        if self.isHovered():
            if self.x <= self.canvas.mouseX <= self.x + len(self.sprite[self.canvas.mouseY - self.y]):
                i = (self.canvas.mouseY - self.y) + self.i
                self.onElementHovered(i)
                self.canvas.isHovering = True

    @property
    def list(self):
        newList = self.canvas.context.eval(self.listProperty)
        if self.i > len(newList) - self.height or self.followTail:
            self.i = max(len(newList) - self.height, 0)
        return newList

    @property
    def sprite(self):
        sprite = [self.reprFunction(e) for e in self.list[self.i:self.i + self.height]]
        sprite += (self.height - len(sprite)) * ['']
        if len(self.list) > self.height:
            sprite[0] += (self.width - len(sprite[0])) * ' ' + '↑'
            sprite[len(sprite) - 1] += (self.width - len(sprite[len(sprite) - 1])) * ' ' + '↓'
        return sprite
