import pygame
import scripts.Engine as E


class Coin:
    def __init__(self, image: pygame.Surface, x, y, vel):
        self.rect = image.get_rect(topleft=(x, y))
        self.image = image
        self.physics_obj = E.Physics(x, y, self.rect.width, self.rect.height)
        self.movement = vel

        self.retardation = 0.08
        self.grav = 0.2

    def draw(self, surf, scroll):
        surf.blit(self.image, (self.rect.x-scroll[0], self.rect.y-scroll[1]))

    def update(self, tiles):
        collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
        self.rect.x = self.physics_obj.rect.x
        self.rect.y = self.physics_obj.rect.y

        if collisions["bottom"]:
            self.movement[1] *= -0.65
            if abs(self.movement[1]) <= 0.65:
                self.movement[1] = 0.1

        if self.movement[0] > 0:
            self.movement[0] = max(0, self.movement[0]-self.retardation)
        else:
            self.movement[0] = min(0, self.movement[0]+self.retardation) 

        self.movement[1] += self.grav




