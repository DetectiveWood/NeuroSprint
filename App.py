from UI import UI
import pygame
import sys
pygame.init()

class App:
    IS_RUN = True
    def __init__(self):
        self.ui = UI()
        self.connectSignals()

    def update(self):
        self.ui.update()

    def run(self):
        while self.IS_RUN:
            self.update()

    def connectSignals(self):
        self.ui.mainWin.closeSignal.connect(self.close)

    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    app = App()
    app.run()
