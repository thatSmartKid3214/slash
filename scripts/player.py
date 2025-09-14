import pygame
import scripts.Engine as E
from scripts.entity import HurtableEntity

class Player(HurtableEntity):
    def __init__(self, x, y, width, height, vel, jump_height, gravity, health):
        super().__init__(x, y, width, height, vel, jump_height, gravity, health, hurt_time=0.4)

        self.attacking = False
        self.flip = False

        self.max_vel_y = 7
        self.jump_count = 0
        self.max_jumps = 1
        self.grounded = False
        self.retardation = 0.2
        self.state = "idle"

        self.on_wall = False
        self.wall_jumping = False
        self.wall_jump_timer = E.Timer(0.25)
        self.wall_jump_speed = self.vel
        self.direction = 1
        self.speed_boost = False
        self.slowing_down = False
        self.big_jump = False
        self.leaping = False
        self.speed_multiplier = 2.6

    def jump(self):

        if self.leaping:
            return
        
        if not self.on_wall:
            # The first jump should be when the player is grounded
            if self.jump_count == 0:
                if not self.grounded:
                    return

            if self.jump_count >= 0 and self.jump_count < self.max_jumps:
                if not self.slowing_down:
                    self.grounded = False
                    self.vel_y = -self.jump_height
                    self.jump_count += 1
                    self.state = "jump"
                else:
                    if abs(self.movement[0] < self.vel*self.speed_multiplier*0.3):
                        self.grounded = False
                        self.vel_y = -self.jump_height*1.3
                        self.jump_count = self.max_jumps
                        self.big_jump = True
                        
                        if self.movement[0] > 0:
                            self.movement[0] = self.vel*0.35
                        else:
                            self.movement[0] = -self.vel*0.35
                    else:
                        self.grounded = False
                        self.vel_y = -self.jump_height
                        self.jump_count += 1
                    
                        self.state = "jump"

        else:
            if not self.speed_boost:
                self.movement[0] = self.wall_jump_speed*self.direction
                self.vel_y = -4.7
                self.jump_count = self.max_jumps - 1
            else:
                self.movement[0] = self.wall_jump_speed*self.speed_multiplier*self.direction
                self.vel_y = -4.4
                self.jump_count = self.max_jumps
            
            self.state = "jump"

            self.wall_jumping = True    
            self.wall_jump_timer.set() 
    
    def leap(self):
        if self.speed_boost:
            self.vel_y = -4
            speed = self.vel * self.speed_multiplier
            if self.movement[0] < 0:
                self.movement[0] = -speed
            else:
                self.movement[0] = speed
            self.leaping = True

    def move(self, tiles):
        speed_mult = 1.0
        if self.speed_boost:
            speed_mult = self.speed_multiplier

        if not (self.big_jump or self.leaping):
            if not (self.wall_jumping or self.speed_boost):
                self.slowing_down = False
                if self.left:
                    self.movement[0] = -self.vel * speed_mult
                    if self.grounded:
                        self.state = "run"
                if self.right:
                    self.movement[0] = self.vel * speed_mult
                    if self.grounded:
                        self.state = "run"
            elif (not self.wall_jumping) and self.speed_boost:
                acceleration = 0.4
                if self.left:

                    if self.movement[0] > 0:
                        acceleration /= 3
                        self.slowing_down = True
                    else:
                        self.slowing_down = False

                    self.movement[0] -= acceleration
                    if self.movement[0] < -self.vel * speed_mult:
                        self.movement[0] = -self.vel * speed_mult
                        if self.grounded:
                            self.state = "run"
                if self.right:
                    if self.movement[0] < 0:
                        acceleration /= 3
                        self.slowing_down = True
                    else:
                        self.slowing_down = False

                    self.movement[0] += acceleration
                    if self.movement[0] > self.vel * speed_mult:
                        self.movement[0] = self.vel * speed_mult
                        if self.grounded:
                            self.state = "run"
            
            self.vel_y += self.gravity
            if self.vel_y >= self.max_vel_y:
                self.vel_y = self.max_vel_y
        else:
            if self.movement[1] > self.max_vel_y*0.7:
                self.big_jump = False
            
            self.vel_y += self.gravity*0.55
            if self.vel_y >= self.max_vel_y:
                self.vel_y = self.max_vel_y
        
        if self.on_wall and self.vel_y > 1:
            self.vel_y = 1.4

        self.movement[1] = self.vel_y

        if self.wall_jumping:
            if self.wall_jump_timer.timed_out():
                self.wall_jumping = False
        
        if self.movement[0] == 0 and self.grounded:
            self.state = "idle"

        self.collisions = self.physics_obj.movement(self.movement, tiles, 1.0)
        self.rect.x = self.physics_obj.rect.x
        self.rect.y = self.physics_obj.rect.y
        

        if self.collisions["bottom"]:
            self.vel_y = 1
            self.jump_count = 0
            self.grounded = True
            self.big_jump = False
            self.leaping = False
        else:
            self.grounded = False

        if self.collisions["top"]:
            self.vel_y = 1

        if (self.collisions["left"] or self.collisions["right"]):
            if not self.grounded:
                self.on_wall = True
                self.state = "wall_slide"
            
            if self.speed_boost and self.grounded:
                self.movement[0] *= 0.2
        else:
            self.on_wall = False
            if not self.grounded:
                self.state = "jump"

        if self.collisions["left"]:
            self.direction = 1
            self.flip = False
        
        if self.collisions["right"]:
            self.direction = -1
            self.flip = True
        
        if not (self.wall_jumping or self.big_jump or self.leaping):
            if self.movement[0] < 0:
                self.movement[0] = min(0, self.movement[0] + self.retardation)
            if self.movement[0] > 0:
                self.movement[0] = max(0, self.movement[0] - self.retardation)
        
        self.wall_jump_timer.update()


    def draw(self, surf, scroll=[0, 0]):
        self.image = self.animation.animate(self.state, True)

        offset_x = 0
        if self.state == "wall_slide" and self.flip:
            offset_x = 2
        E.perfect_outline(pygame.transform.flip(self.image, self.flip, False), surf, (self.rect.x+offset_x-scroll[0],self.rect.y-scroll[1]-3), (20, 20, 20))
        surf.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x+offset_x-scroll[0],self.rect.y-scroll[1]-3))

    def update(self, tiles):
        super().update()
        self.move(tiles)


