import pygame
import os

class CharacterSprite:
    def __init__(self, spritesheet_path, frame_width, frame_height, num_frames, fps=8, scale=2):
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frames = []
        for i in range(num_frames):
            frame = self.spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            if scale != 1:
                frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
            self.frames.append(frame)
        self.current_frame = 0
        self.fps = fps
        self.time_per_frame = 1000 // fps
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.time_per_frame:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.last_update = now

    def draw(self, surface, x, y):
        surface.blit(self.frames[self.current_frame], (x, y))
