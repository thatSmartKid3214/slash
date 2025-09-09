import pygame
import random
import math
from scripts.Engine import blit_center

def slash_outline(img, surf, loc, color, colorkey=(0,0,0), colorkey2=(0,0,0)):
    img.set_colorkey(colorkey)
    mask = pygame.mask.from_surface(img)
    mask_surf = mask.to_surface(setcolor=color)
    mask_surf.set_colorkey((0,0,0))

    blit_center(surf, mask_surf,(loc[0]-1,loc[1]))
    blit_center(surf, mask_surf,(loc[0]+1,loc[1]))
    blit_center(surf, mask_surf,(loc[0],loc[1]-1))
    blit_center(surf, mask_surf,(loc[0],loc[1]+1))

class SlashVFX:
    def __init__(self, x, y, width, height, speed, slash_size, slash_size_change, roll_down_speed, color, radius, angle, shape="circle"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.radius = radius
        self.slash_size = slash_size 
        self.slash_size_change = slash_size_change
        self.shape = shape
        self.angle = angle
        self.active = True
        self.active_count = 0
        self.surface = None

        # Swipe effect for slash
        self.roll_down_speed = roll_down_speed
        self.roll_down = 0

        self.generate_slash()

    
    def generate_slash(self):
        if self.shape == "circle":
            surf_size = (self.radius*2, self.radius*2)

            temp_surf = pygame.Surface(surf_size).convert_alpha()

            pygame.draw.circle(temp_surf, self.color, (self.radius, self.radius), self.radius)
            pygame.draw.circle(temp_surf, (0, 0, 0), (self.slash_size, self.radius), self.radius)
            if self.roll_down <= self.radius*2:
                pygame.draw.rect(temp_surf, (0, 0, 0), (0, self.roll_down, self.radius*2, self.radius*2))

            temp_surf.set_colorkey((0, 0, 0))

            self.surface = pygame.transform.scale(temp_surf, (self.width, self.height))

            self.slash_size += self.slash_size_change
            self.roll_down += self.roll_down_speed
            self.x += math.cos(math.radians(-self.angle))*self.speed
            self.y += math.sin(math.radians(-self.angle))*self.speed

            if self.slash_size >= self.radius:
                self.active = False

    def draw(self, screen, scroll):
        #slash_outline(pygame.transform.rotate(self.surface, self.angle), screen, (self.x-scroll[0], self.y-scroll[1]), (1, 1, 1))
        blit_center(screen, pygame.transform.rotate(self.surface, self.angle), (self.x-scroll[0], self.y-scroll[1]))
        self.generate_slash()

        self.active_count += 1



