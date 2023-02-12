import math

from interface.sprite import *


class Textbox(Sprite):
    def __init__(self, text, x, y, w, onhover=lambda: None, canvas_=None, scrolling=True, scrollingSpeed=200):
        super(Textbox, self).__init__('', x, y, onhover, canvas_)
        self.scrolling = scrolling
        self.scrollingSpeed = scrollingSpeed
        self.sprite = []
        self.text = text
        self.lastFormattedText = text
        self.timeOfLastTextChange = 0
        self.currentIndex = len(self.text) if not scrolling else 0
        self.w = w

    def onAdd(self):
        self.timeOfLastTextChange = self.canvas.t

    def update(self):
        super(Textbox, self).update()
        formattedText = self.canvas.context.eval(f"""f'''{self.text}'''""")
        if formattedText != self.lastFormattedText:
            self.currentIndex = 0
            self.timeOfLastTextChange = self.canvas.t
        elif self.currentIndex != -1:
            self.currentIndex = round((self.canvas.t - self.timeOfLastTextChange) * self.scrollingSpeed)
        self.sprite = ['']
        i = 0
        scrolledFormattedText = formattedText[:self.currentIndex] if self.scrolling else formattedText
        splitText = scrolledFormattedText.split()
        while len(splitText) > 0:
            if len(self.sprite[i]) + len(splitText[0]) > self.w:
                self.sprite[i] = self.sprite[i].strip()
                spacesToAdd = self.w - len(self.sprite[i])
                spaces = self.sprite[i].count(' ')
                extraSpacesPerSpace = spacesToAdd / spaces
                newSprite = ''
                spacesAdded = 0
                for char in self.sprite[i]:
                    if char == ' ' and spacesAdded < spacesToAdd:
                        newSprite += (1 + math.ceil(extraSpacesPerSpace)) * ' '
                        spacesAdded += math.ceil(extraSpacesPerSpace)
                    else:
                        newSprite += char
                self.sprite[i] = newSprite
                i += 1
                self.sprite.append('')
            else:
                self.sprite[i] += (splitText.pop(0) + ' ')
        self.lastFormattedText = formattedText
