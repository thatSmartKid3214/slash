import pygame


class Window():
    def __init__(self, width, height, caption, display=None, opengl_enabled=False):
        self.width = width
        self.height = height
        self.caption = caption
        self.use_opengl = opengl_enabled
        self.display = display # If a surface is passed, everything will be rendered on that and will be upscaled

        self.window = pygame.display.set_mode((self.width, self.height), pygame.SCALED)
        pygame.display.set_caption(self.caption)
    
    def fill(self, fill_color):
        if self.display != None:
            self.display.fill(fill_color)
        self.window.fill(fill_color)

    def get_display(self):
        return self.display

    def get_surface(self):
        return self.window
    
    def update(self):
        if self.display:
            self.window.blit(pygame.transform.scale(self.display, (self.width, self.height)), (0, 0))

        pygame.display.update()
    
    @property
    def events(self):
        return pygame.event.get()
        


