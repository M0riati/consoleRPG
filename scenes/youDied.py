from asciimatics.renderers import FigletText

from interface import *

youdiedText = FigletText("Y O U   D I E D", font='POISON')


class YouDied(Scene):
    def __init__(self):
        super(YouDied, self).__init__()
        self.musicPath = 'assets/audio/music/clairDeLune.ogg'
        self.sprites = [
            ColorMappedSprite(
                youdiedText.rendered_text[0],
                0, 0, kwargs={'@': 1, '!': 1, ':': 7},
            ),
            Button(
                ['[Accept your Fate]'],
                (youdiedText.max_width - len('[Accept your Fate]')) // 2, youdiedText.max_height + 2,
                onclick=lambda: self.canvas.stop(), color=Screen.COLOUR_MAGENTA
            )
        ]
