class TextAlign:
    ALIGN_CENTER = 0
    ALIGN_LEFT = 0
    ALIGN_RIGHT = 0

class BorderStyle:
    def __init__(self):
        self.COLOR : tuple = (255,100,100)
        self.DISABLED_COLOR : tuple = (0,0,0)
        self.PRESED_COLOR : tuple = (0,0,0)
        self.HOVER_COLOR : tuple = (100,100,100)
        self.BORDER_SIZE : int = 1
        self.BORDER_RADIUS : int = 0
        self.BORDER_COLOR : tuple = (0,0,0)

class Padding:
    def __init__(self, left=1, right=1, bottom=1, top=1):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top

    def __getitem__(self, index):
        return [self.left, self.right, self.bottom, self.top][index]
    
    def __setitem__(self, index, value):
        values = [self.left, self.right, self.bottom, self.top]
        values[index] = value
        self.left, self.right, self.bottom, self.top = values

class Widget:
    def __init__(self):
        self.x : int = 0
        self.y : int = 0 
        self.width : int
        self.height : int
        self.padding : Padding = Padding()
        self.size : int = 1

    def update(self):
        pass

    def check_events(self,event):
        pass

    def resize(self):
        pass