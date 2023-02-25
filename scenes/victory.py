from asciimatics.renderers import FigletText

from interface import *

victoryText = FigletText("V I C T O R Y", font='ROMAN')


class Victory(Scene):
    def __init__(self):
        super().__init__()
        self.tracklist = ['assets/audio/music/fanfare.ogg']
        self.loopEnabled = False
        self.sprites = [
            Sprite(
                victoryText.rendered_text[0],
                0, 0
            ),
            Button(
                ['[Continue]'],
                (victoryText.max_width - len('[Continue]')) // 2, victoryText.max_height + 2,
                onclick=lambda: self.canvas.stop(), color=Screen.COLOUR_RED
            )
        ]
