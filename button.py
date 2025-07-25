import pygame

class StoneButton:
    def __init__(self, text, pos, size, sound):
        self.text = text
        self.pos = pos
        self.size = size
        self.sound = sound
        self.base_rect = pygame.Rect(pos, size)
        self.rect = self.base_rect.copy()
        self.hovered = False
        self.clicked = False
        self.font = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 32)
        self.base_color = (110, 110, 110)
        self.edge_color = (70, 70, 70)
        self.text_color = (255, 255, 210)
        self.grow_scale = 1.1

    def draw(self, screen):
        color = self.base_color
        rect = self.rect
        pygame.draw.rect(screen, color, rect, border_radius=18)
        pygame.draw.rect(screen, self.edge_color, rect, width=6, border_radius=18)
        text_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surf, (rect.centerx - text_surf.get_width()//2, rect.centery - text_surf.get_height()//2))

    def update(self, mouse_pos):
        if self.base_rect.collidepoint(mouse_pos):
            if not self.hovered:
                self.rect = self.base_rect.inflate(
                    int(self.size[0] * (self.grow_scale - 1)),
                    int(self.size[1] * (self.grow_scale - 1))
                )
                self.rect.center = self.base_rect.center
                self.hovered = True
        else:
            if self.hovered:
                self.rect = self.base_rect.copy()
            self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.sound.play()
            self.clicked = True
