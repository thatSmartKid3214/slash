import pygame
import math
from scripts.Engine import Physics, blit_center

class PhysicsProjectile:
    def __init__(self, image, owner, damage, x, y, width, height, grav, vel):
        self.image = image
        self.owner = owner
        self.dmg = damage
        self.x = x
        self.y = y
        self.rect = pygame.FRect(x, y, width, height)
        self.physics_obj = Physics(x, y, width, height)
        self.gravity = grav
        self.movement = vel
        self.retardation = 0

        self.active = True

        self.bounce_count = 0
        self.max_bounces = 2

    def draw(self, surf, scroll):
        surf.blit(self.image, (self.rect.x-scroll[0], self.rect.y-scroll[1]))
    
    def update(self, tiles):
        collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
        self.rect.x = self.physics_obj.rect.x
        self.rect.y = self.physics_obj.rect.y

        if collisions["left"] or collisions["right"]:
            self.movement[0] *= -0.75

        if collisions["bottom"]:
            self.movement[1] *= -0.7
            self.bounce_count += 1

            if self.bounce_count > self.max_bounces:
                self.active = False

        if self.movement[0] > 0:
            self.movement[0] = max(0, self.movement[0]-self.retardation)
        else:
            self.movement[0] = min(0, self.movement[0]+self.retardation) 

        self.movement[1] += self.gravity

class Projectile:
    def __init__(self, image, owner, damage, x, y, width, height, speed, angle):
        self.image = image
        self.owner = owner
        self.dmg = damage
        self.x = x
        self.y = y
        self.rect = pygame.FRect(x, y, width, height)
        self.physics_obj = Physics(x, y, width, height)
        self.speed = speed
        self.angle = angle

        self.movement = [math.cos(self.angle)*self.speed, math.sin(self.angle)*self.speed]

        self.active = True

    def draw(self, surf, scroll):
        blit_center(surf, pygame.transform.rotate(self.image, -math.degrees(self.angle)), (self.rect.x-scroll[0], self.rect.y-scroll[1]))
    
    def update(self, tiles):
        collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
        self.rect.x = self.physics_obj.rect.x
        self.rect.y = self.physics_obj.rect.y

        if collisions["top"] or collisions["bottom"] or collisions["left"] or collisions["right"]:
            self.active = False

