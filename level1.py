import pygame
import os
from settings import WIDTH, HEIGHT

class LevelOneScreen:
    def __init__(self, screen):
        self.screen = screen
        self.layers = []
        # Carga las 10 capas automáticamente (background_0.png a background_9.png)
        for i in range(10):
            filename = f"background_{i}.png"
            path = os.path.join("assetts/images/level1/background", filename)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
            self.layers.append(img)

    def draw(self):
        for layer in self.layers:
            self.screen.blit(layer, (0, 0))

    def update(self):
        pass

    def handle_event(self, event):
        pass
