# background.py
import pygame
import os

class Background:
    def __init__(self, folder_path, fps=10):
        self.frames = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.png'):
                path = os.path.join(folder_path, filename)
                img = pygame.image.load(path).convert()
                self.frames.append(img)
        self.current_frame = 0
        self.total_frames = len(self.frames)
        self.fps = fps
        self.frame_duration = 1000 // fps
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.last_update = now

    def draw(self, screen):
        if self.frames:
            frame = self.frames[self.current_frame]
            # Tamaño original del frame
            fw, fh = frame.get_width(), frame.get_height()
            # Tamaño de la ventana
            sw, sh = screen.get_width(), screen.get_height()

            # Calcular escala para mantener relación de aspecto
            scale = min(sw / fw, sh / fh)
            new_w, new_h = int(fw * scale), int(fh * scale)
            frame_scaled = pygame.transform.scale(frame, (new_w, new_h))

            # Centrar la imagen (letterbox)
            x = (sw - new_w) // 2
            y = (sh - new_h) // 2

            screen.fill((0,0,0))  # Fondo negro si sobran bordes
            screen.blit(frame_scaled, (x, y))

        
        