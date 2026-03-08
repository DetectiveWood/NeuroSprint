from Graphic.Widgets.Layout import LayoutH,LayoutV
from Graphic.Widgets.Button import Button
from Graphic.Widgets.Widget import Widget
from Signal import Signal
import pygame

class WindowParams:
    WINDOW_WIDTH : int = 800
    WINDOW_HEIGHT : int = 600
    BACKGROUND_COLOR : tuple = (255, 255, 255)
    WINDOW_TITLE : str = "Мое окно Pygame"

class WindowStates:
    CLOSE = -1
    EMPTY = 0
    RESIZE = 2
    MOVE = 3

class Window: 
    SCREEN = pygame.display.set_mode((WindowParams.WINDOW_WIDTH, WindowParams.WINDOW_HEIGHT), pygame.RESIZABLE)
    def __init__(self):
        self.closeSignal = Signal()
        self.state : WindowStates = WindowStates.EMPTY
        self.mainLayout = LayoutH()
        self.mainLayout.x = 0
        self.mainLayout.y = 0
        self.mainLayout.width = WindowParams.WINDOW_WIDTH
        self.mainLayout.height = WindowParams.WINDOW_HEIGHT
        pygame.display.set_caption(WindowParams.WINDOW_TITLE)
        self.setTestScreen()

    def setTestScreen(self):
        empty = Widget()
        bt1 = Button('asd')
        bt1.style.COLOR = (100,100,255)
        bt1.size = 2
        bt1.style.BORDER_STYLE.BORDER_RADIUS = 50
        bt1.style.BORDER_STYLE.BORDER_SIZE = 10
        self.mainLayout.add_widget(empty)
        self.layout = LayoutV()
        self.mainLayout.add_widget(self.layout)
        self.layout.add_widget(bt1)
        bt2 = Button()
        self.layout.add_widget(bt2)

    def check_event(self):
        for event in pygame.event.get():
            self.mainLayout.check_events(event)
            if event.type == pygame.QUIT:
                self.state = WindowStates.CLOSE
                self.closeSignal.emit()
            elif event.type == pygame.VIDEORESIZE:
                WindowParams.WINDOW_WIDTH = event.w
                WindowParams.WINDOW_HEIGHT = event.h
                self.resize()
                print(f"Новый размер: {event.w} x {event.h}")

    def resize(self):
        self.mainLayout.width = WindowParams.WINDOW_WIDTH
        self.mainLayout.height = WindowParams.WINDOW_HEIGHT
        self.mainLayout.resize()

    def draw(self):
        self.SCREEN.fill(WindowParams.BACKGROUND_COLOR)
        self.mainLayout.update()
        pygame.display.flip()

    def update(self):
        self.check_event()
        self.draw()