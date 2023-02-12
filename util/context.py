class Context:
    def __init__(self, locals_, globals_):
        self.locals = locals_
        self.globals = globals_

    def eval(self, _source):
        return eval(_source, self.globals, self.locals)
