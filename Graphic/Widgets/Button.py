from Graphic.Widgets.Widget import Widget, TextAlign, BorderStyle
from Signal import Signal
import pygame

class ButtonStatus:
    DISABLED = -1
    START = 0
    HOVER  = 1
    PRESSED = 2
    RELEASED = 3

class ButtonStyles:
    def __init__(self):
        self.COLOR : tuple = (0,0,0)
        self.DISABLED_COLOR : tuple = (0,0,0)
        self.PRESED_COLOR : tuple = (0,0,0)
        self.HOVER_COLOR : tuple = (100,100,100)
        self.TEXT_COLOR : tuple = (255,255,255)
        self.TEXT_ALIGN : TextAlign = TextAlign.ALIGN_CENTER
        self.FONT_SIZE : int = 36
        self.BORDER_STYLE : BorderStyle = BorderStyle()


class Button(Widget):
    def __init__(self,text : str = '',x:int = 0,y:int = 0,size:int = 1):
        super().__init__()
        self.clicked = Signal()
        self.released = Signal()
        self.hover = Signal()
        self.x = x
        self.y = y
        self.size = size
        self.text : str = text
        self.style : ButtonStyles = ButtonStyles()
        self.status : ButtonStatus = ButtonStatus.START
        self.font = pygame.font.Font(None, self.style.FONT_SIZE)
        self.is_hover = 0
        

    def set_text(self,text):
        self.text = text

    def resize(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.font = pygame.font.Font(None, self.style.FONT_SIZE)

    def check_events(self,event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(mouse_pos) and self.status != ButtonStatus.PRESSED: 
            self.status = ButtonStatus.PRESSED
            self.clicked.emit()
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(mouse_pos): 
            self.status = ButtonStatus.RELEASED
            self.released.emit()
        if (self.status == ButtonStatus.START or self.status == ButtonStatus.RELEASED) and self.rect.collidepoint(mouse_pos):
            self.status = ButtonStatus.HOVER
            if not(self.is_hover):
                self.is_hover = 1
                self.hover.emit(True)
        elif not(self.rect.collidepoint(mouse_pos)) and self.status != ButtonStatus.START:
            self.status = ButtonStatus.START
            self.is_hover = 0
            self.hover.emit(False)

    def drawRect(self):
        from Graphic.window import Window
        BodyColor:tuple = (255,255,255)
        BorderColor:tuple = (255,255,255)
        if self.status == ButtonStatus.DISABLED:
            BodyColor = self.style.DISABLED_COLOR
            BorderColor = self.style.BORDER_STYLE.DISABLED_COLOR
        elif self.status == ButtonStatus.START:
            BodyColor = self.style.COLOR
            BorderColor = self.style.BORDER_STYLE.COLOR
        elif self.status == ButtonStatus.HOVER:
            BodyColor = self.style.HOVER_COLOR
            BorderColor = self.style.BORDER_STYLE.HOVER_COLOR
        elif self.status == ButtonStatus.PRESSED:
            BodyColor = self.style.PRESED_COLOR
            BorderColor = self.style.BORDER_STYLE.PRESED_COLOR
        pygame.draw.rect(Window.SCREEN, BodyColor, self.rect, border_radius=self.style.BORDER_STYLE.BORDER_RADIUS)
        pygame.draw.rect(Window.SCREEN, BorderColor, self.rect,self.style.BORDER_STYLE.BORDER_SIZE, border_radius=self.style.BORDER_STYLE.BORDER_RADIUS)

    def drawText(self):
        from Graphic.window import Window
        text_surface = self.font.render(self.text, True, self.style.TEXT_COLOR)
        if self.style.TEXT_ALIGN == TextAlign.ALIGN_CENTER:
            text_rect = text_surface.get_rect(center=self.rect.center)
        Window.SCREEN.blit(text_surface, text_rect)

    def draw(self):
        self.drawRect()
        self.drawText()

    def update(self):
        self.draw()
