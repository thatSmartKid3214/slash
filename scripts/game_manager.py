import pygame
import json
import math
import scripts.Engine as E

from scripts.player import Player
from scripts.weapon import *

TILESIZE = 16

class GameManager:
    def __init__(self, game):
        self.game = game
        self.win_surf = self.game.window.get_display()

        self.width_ratio = self.game.window.win_disp_width_ratio()
        self.height_ratio = self.game.window.win_disp_height_ratio()
        
        self.cam = E.Camera()

        self.level = {}
        self.tiles = {}
        self.camera_bounds = []
        self.current_level = 1

        self.render_layers = ["background", "decor", "tiles", "player", "slashes", "foreground"]

        self.spawn_pos = [0, 0]
        self.load_level("data/levels/debug2.lvl")
        self.player = Player(self.spawn_pos[0], self.spawn_pos[1], TILESIZE, TILESIZE, 3.4, 6, 0.32, 100)
        weapon = Weapon(self.game.assets.get_image("worn katana"), self.game.assets.get_weapon("worn katana"))
        self.player.weapon = weapon

        self.slashes = []

        # Debug stuff
        self.debug_font = pygame.font.SysFont("Verdana", 15, True)

    def load_level(self, level):
        with open(level) as file:
            data = json.load(file)
            file.close()

        self.level = data["level"]

        for tile_id in self.level["tiles"]:
            tile = self.level["tiles"][tile_id]
            self.tiles[tile_id] = pygame.Rect(tile[2][0]*TILESIZE, tile[2][1]*TILESIZE, TILESIZE, TILESIZE)

        self.bounds = [data["bounds"]["left"], data["bounds"]["top"], data["bounds"]["right"], data["bounds"]["bottom"]]

        for obj in data["objects"]:
            # do stuff
            if obj["name"] == "Spawn":
                self.spawn_pos = [obj["rect"][0], obj["rect"][1]]

    def manage_states(self):
        pass

    def play_game(self):
        self.game.window.fill((127, 127, 127))
        self.game.clock.tick(self.game.FPS)

        mouse_pos = pygame.mouse.get_pos()
        display_pos = [mouse_pos[0]/self.width_ratio, mouse_pos[1]/self.height_ratio]

        self.cam.update(self.player.rect, self.win_surf, 1, 1.0)

        pos = E.world_to_screen(self.player.rect.center, self.cam.scroll)
        angle = E.angle_from_points(pos, display_pos)
        angle_deg = math.degrees(angle)

        cam_view = [self.cam.scroll[0], self.cam.scroll[1], self.cam.scroll[0]+self.win_surf.get_width(), self.cam.scroll[1]+self.win_surf.get_height()]

        if self.game.joystick != None:
            axis = self.game.joystick.get_axis(0)

            if axis > -0.08 and axis < 0.08:
                axis = 0
                self.player.left = False
                self.player.right = False

            if axis != 0:
                if axis > 0:
                    self.player.right = True
                    self.player.left = False
                if axis < 0:
                    self.player.left = True
                    self.player.right = False
        

        for event in self.game.window.events:
            if event.type == pygame.QUIT:
                self.game.quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.left = True
                if event.key == pygame.K_d:
                    self.player.right = True
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_v:
                    self.player.leap()
                if event.key == pygame.K_f:
                    self.player.speed_boost = not self.player.speed_boost
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.player.left = False
                if event.key == pygame.K_d:
                    self.player.right = False
            
            if event.type == pygame.JOYDEVICEADDED:
                self.game.joystick = pygame.joystick.Joystick(event.device_index)

            if event.type == pygame.JOYDEVICEREMOVED:
                self.game.joystick = None
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.player.jump()

        self.player.move(list(self.tiles.values()))

        self.player.attacking = False
        if pygame.mouse.get_pressed()[0]:
            self.player.attacking = True
            self.player.weapon.attack(self.player.rect.center, -angle_deg+random.randint(-3, 3), self.player, self.slashes, display_pos[0]<pos[0])
        
        # Draw level
        for layer in self.render_layers:
            if layer == "player":
                self.player.draw(self.win_surf, self.cam.scroll)
                if not self.player.attacking:
                    self.player.weapon.draw(self.player.rect.center, -angle_deg, self.win_surf, self.cam.scroll)

                self.player.weapon.update()

                #state = self.debug_font.render(self.player.state, False, (0, 0, 0))
                #self.win_surf.blit(state, (self.player.rect.x-self.cam.scroll[0], self.player.rect.y - self.cam.scroll[1] - 15))
            elif layer == "slashes":
                for i, slash in sorted(enumerate(self.slashes), reverse=True):
                    slash.draw(self.win_surf, self.cam.scroll)

                    if slash.active_count > slash.lifetime:
                        slash.active = False

                    if not slash.active:
                        self.slashes.pop(i)
            else:
                for tile_id in self.level[layer]:
                    tile = self.level[layer][tile_id]
                    pos = [tile[2][0]*TILESIZE, tile[2][1]*TILESIZE]

                    if (pos[0] > cam_view[0]-TILESIZE-1 and pos[0] < cam_view[2]+1) and (pos[1] > cam_view[1]-TILESIZE-1 and pos[1] < cam_view[3]+1):
                        
                        self.win_surf.blit(self.game.assets.get_tile(tile[0], tile[1]), (pos[0]-self.cam.scroll[0], pos[1]-self.cam.scroll[1]))
        

        self.game.window.update()
    
    def run(self):
        self.play_game()
