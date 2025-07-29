import pygame
import os

class EnemySprite:
    def __init__(self, path, scale=2):
        self.animations = {}
        self.load_animations(path, scale)
        self.current_action = "Idle"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.current_action][0]
        self.rect = self.image.get_rect(topleft=(700, 400))  # posición inicial enemiga
        self.timer = 0

    def load_animations(self, path, scale):
        actions = ["Idle", "Walk", "Attack", "Hurt", "Dead"]
        for action in actions:
            action_path = os.path.join(path, f"{action}.png")
            if os.path.exists(action_path):
                sheet = pygame.image.load(action_path).convert_alpha()
                frame_width = sheet.get_width() // 4  # asumiendo 4 frames por hoja
                frame_height = sheet.get_height()
                frames = []
                for i in range(4):
                    frame = sheet.subsurface(pygame.Rect(i*frame_width, 0, frame_width, frame_height))
                    frame = pygame.transform.scale(frame, (frame_width*scale, frame_height*scale))
                    frames.append(frame)
                self.animations[action] = frames

    def update(self):
        self.timer += self.animation_speed
        if self.timer >= len(self.animations[self.current_action]):
            self.timer = 0
        self.current_frame = int(self.timer)
        self.image = self.animations[self.current_action][self.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
