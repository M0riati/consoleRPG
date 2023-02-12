from asciimatics.screen import Screen

from interface import sprite


class Button(sprite.Sprite):
    def __init__(self, sprite_, x, y, onclick=lambda: None, onhover=lambda: None, canvas_=None,
                 color=Screen.COLOUR_WHITE):
        super(Button, self).__init__(sprite_, x, y, onhover, canvas_, color)
        self.onclick = onclick

    def update(self):
        super(Button, self).update()
        if self.isClicked():
            self.canvas.leftClick = False
            self.onclick()
