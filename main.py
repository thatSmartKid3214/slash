import pygame
import scripts

pygame.init()
pygame.font.init()
pygame.joystick.init()

class Game:
    def __init__(self):
        display = pygame.Surface((480, 270))
        self.window = scripts.Window(480*2, 270*2, "Slash", display)
        self.clock = pygame.time.Clock()
        self.joystick = None
        self.FPS = 60

        self.running = True

        self.assets = scripts.Assets()
        self.gm = scripts.GM(self)

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            self.gm.run()

game = Game()
game.run()

pygame.quit()


