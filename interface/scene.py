from util import context


class Scene:
    def __init__(self):
        self.sprites = []
        self.context = context.Context(locals(), globals())
        self.onnothover = lambda: None
        self.canvas = None
        self.musicPath = None

    def keyboardInput(self, event):
        pass

    def update(self):
        pass
