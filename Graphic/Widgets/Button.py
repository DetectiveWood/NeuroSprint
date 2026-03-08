from Graphic.Widgets.Widget import Widget

import pygame

class ButtonStatus:
    DISABLED = -1
    START = 0
    HOVER  = 1
    PRESSED = 2
    RELEASED = 3

class ButtonTextAlign:
    ALIGN_CENTER = 0
    ALIGN_LEFT = 0
    ALIGN_RIGHT = 0

class ButtonStyles:
    COLOR : tuple = (0,0,0)
    DISABLED_COLOR : tuple = (0,0,0)
    PRESED_COLOR : tuple = (0,0,0)
    HOVER_COLOR : tuple = (100,100,100)
    TEXT_COLOR : tuple = (255,255,255)
    TEXT_ALIGN : ButtonTextAlign = ButtonTextAlign.ALIGN_CENTER
    FONT_SIZE : int = 36


class Button(Widget):
    def __init__(self,text : str = '',x:int = 0,y:int = 0,size:int = 1):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.text : str = ''
        self.style : ButtonStyles = ButtonStyles()
        self.status : ButtonStatus = ButtonStatus.START

    def set_text(self,text):
        self.text = text

    def resize(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def check_event(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.status == ButtonStatus.START and self.rect.collidepoint(mouse_pos):
            pass


    def drawRect(self):
        from Graphic.window import Window
        color:tuple = (255,255,255)
        if self.status == ButtonStatus.DISABLED:
            color = self.style.DISABLED_COLOR
        elif self.status == ButtonStatus.START:
            color = self.style.COLOR
        elif self.status == ButtonStatus.HOVER:
            color = self.style.HOVER_COLOR
        elif self.status == ButtonStatus.PRESSED:
            color = self.style.PRESED_COLOR
        pygame.draw.rect(Window.SCREEN, color, self.rect)

    def drawText(self):
        pass

    def draw(self):
        self.drawRect()
        self.drawText()
        # print('[lol]')

    def update(self):
        self.check_event()
        self.draw()
