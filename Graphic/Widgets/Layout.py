from Graphic.Widgets.Widget import Widget

class LayoutH(Widget):
    def __init__(self):
        super().__init__()
        self.children : list[Widget] = []
        self.size:int = 1
        self.Space:int = 1

    def calc_size(self):
        size_OC = self.width / self.Space
        print(f"self.width:{self.width},self.size:{self.Space},self.width / self.size:{self.width / self.Space}")
        for child in self.children:
            child.width = (child.size*size_OC)-(child.padding.left + child.padding.right)
            child.height = self.height-(child.padding.top + child.padding.bottom)
            child.x = (self.x + ((child.size*size_OC)* (self.children.index(child)))+child.padding.left)
            print(f"child:{child}, self.children.index(child): {self.children.index(child)}, self.x:{self.x},child.x: {child.x }")
            child.y = self.y +child.padding.top
            child.resize()

    def add_widget(self, widget : Widget):
        self.children.append(widget)
        self.Space = 0 
        for child in self.children:
            self.Space+=child.size
        self.calc_size()

    def resize(self):
        print("resize")
        self.calc_size()

    def update(self):
        for child in self.children:
            child.update()

class LayoutV(Widget):
    def __init__(self):
        super().__init__()
        self.children : list[Widget] = []
        self.Space:int = 1
        self.size = 1

    def calc_size(self):
        size_OC = self.height / self.Space
        for child in self.children:
            child.height = (child.size*size_OC)-(child.padding.top + child.padding.bottom)
            child.width = (self.width)-(child.padding.left + child.padding.right)
            child.x = self.x +child.padding.left
            child.y = self.y + ((child.size*size_OC)* self.children.index(child))+child.padding.top
            child.resize()

    def add_widget(self, widget : Widget):
        self.children.append(widget)
        print(123)
        self.Space = 0 
        for child in self.children:
            self.Space+=child.size
        print(f"size:{self.Space}")
        self.calc_size()

    def resize(self):
        print("resize")
        self.calc_size()

    def update(self):
        for child in self.children:
            child.update()