import pygame
import json
import scripts.Engine as E

from scripts.player import Player

TILESIZE = 16

class GameManager:
    def __init__(self, game):
        self.game = game
        self.win_surf = self.game.window.get_display()
        
        self.cam = E.Camera()

        self.level = {}
        self.tiles = {}
        self.camera_bounds = []
        self.current_level = 1

        self.render_layers = ["background", "decor", "tiles", "player", "foreground"]

        self.spawn_pos = [0, 0]
        self.load_level("data/levels/debug.lvl")
        
        self.player = Player(self.spawn_pos[0], self.spawn_pos[1], TILESIZE, TILESIZE, 3.4, 6, 0.32, 100)

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

        self.cam.update(self.player.rect, self.win_surf, 1, 1.0)

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
        
        # Draw level
        for layer in self.render_layers:
            if layer == "player":
                self.player.draw(self.win_surf, self.cam.scroll)

                #state = self.debug_font.render(self.player.state, False, (0, 0, 0))
                #self.win_surf.blit(state, (self.player.rect.x-self.cam.scroll[0], self.player.rect.y - self.cam.scroll[1] - 15))
            else:
                for tile_id in self.level[layer]:
                    tile = self.level[layer][tile_id]
                    pos = [tile[2][0]*TILESIZE, tile[2][1]*TILESIZE]
                    pygame.draw.rect(self.win_surf, (255, 255, 255), (pos[0]-self.cam.scroll[0], pos[1]-self.cam.scroll[1], TILESIZE, TILESIZE))
        

        self.game.window.update()
    
    def run(self):
        self.play_game()
