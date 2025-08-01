# player.py
import pygame

class Player:
    def __init__(self, sprite, x, y):
        self.sprite = sprite  # pygame.Surface (la imagen del personaje)
        self.x = x
        self.y = y
        self.speed = 6  # Velocidad de movimiento

    def move(self, dx):
        self.x += dx

    def draw(self, surface, offset_x=0):
        # Dibuja el sprite con el offset del scroll
        surface.blit(self.sprite, (self.x - offset_x, self.y))
