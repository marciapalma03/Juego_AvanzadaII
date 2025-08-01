import pygame

class PauseButton:
    def __init__(self, pos, size, sound_click):
        self.image = pygame.image.load("assets/images/ui/pause_icon.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, size)
        self.rect = pygame.Rect(pos, size)
        self.hovered = False
        self.clicked = False
        self.sound_click = sound_click

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        if self.hovered:
            # Un efecto glow simple al pasar el mouse
            glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255,255,160,100), glow.get_rect())
            surface.blit(glow, self.rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.sound_click.play()
            self.clicked = True
