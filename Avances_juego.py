import pygame
import sys
import random
import math
import os

# Inicializar pygame y mixer
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('musicainicio.mp3')
pygame.mixer.music.play(-1)  # -1 significa que se repite en bucle
try:
    sonido_seleccion = pygame.mixer.Sound('Sonidoseleccionpersonaje.mp3')
except:
    print("Error cargando el sonido 'Sonidoseleccionpersonaje.mp3'")
    sonido_seleccion = None

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("THE LEGACY OF THE MIST")

# ----------- COLORES OSCUROS -----------
DARK_BG = (25, 25, 32)
DARKER_BG = (16, 16, 24)
DARK_BTN = (44, 44, 56)
HOVER_BTN = (90, 90, 110)
CLICK_BTN = (170, 170, 190)
NODE_UNLOCK = (140, 140, 150)
NODE_LOCK = (50, 50, 60)
NODE_SEL = (210, 210, 230)

# ------ FONDO DE LA INTERFAZ ------
try:
    fondo_interfaz = pygame.image.load('fondo_menu.png').convert()
    fondo_interfaz = pygame.transform.scale(fondo_interfaz, (WIDTH, HEIGHT))
except:
    fondo_interfaz = pygame.Surface((WIDTH, HEIGHT))
    fondo_interfaz.fill(DARK_BG)

try:
    TITLE_FONT = pygame.font.Font('epic_font.ttf', 56)
except:
    TITLE_FONT = pygame.font.SysFont('Arial', 56, bold=True)
try:
    BUTTON_FONT = pygame.font.Font('button_font.ttf', 36)
except:
    BUTTON_FONT = pygame.font.SysFont('Arial', 36, bold=True)
WHITE = (240, 240, 240)
BLACK = (10, 10, 10)

NUM_FOGS = 25
fog_particles = []
for _ in range(NUM_FOGS):
    x = random.randint(-200, WIDTH+200)
    y = random.randint(0, HEIGHT)
    radius = random.randint(60, 180)
    speed = random.uniform(0.2, 0.7)
    alpha = random.randint(60, 110)
    fog_particles.append([x, y, radius, speed, alpha])

def draw_fog(surface, camera_x=0):
    for i, (x, y, radius, speed, alpha) in enumerate(fog_particles):
        fog_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(fog_surface, (110, 110, 110, alpha), (radius, radius), radius)
        surface.blit(fog_surface, (x - radius - camera_x//3, y - radius))
        fog_particles[i][0] += speed
        if fog_particles[i][0] - radius > WIDTH*3:
            fog_particles[i][0] = -radius
            fog_particles[i][1] = random.randint(0, HEIGHT)
            fog_particles[i][2] = random.randint(60, 180)
            fog_particles[i][4] = random.randint(60, 110)

class AnimatedButton:
    def __init__(self, rect, text, font, sonido=True):
        self.base_rect = pygame.Rect(rect)
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = DARK_BTN
        self.hover_color = HOVER_BTN
        self.click_color = CLICK_BTN
        self.current_color = self.base_color
        self.hovered = False
        self.clicked = False
        self.sonido = sonido  # ← NUEVO

    def draw(self, surface):
        scale = 1.07 if self.hovered else 1.0
        if self.clicked:
            scale = 1.15
        new_width = int(self.base_rect.width * scale)
        new_height = int(self.base_rect.height * scale)
        self.rect.width = new_width
        self.rect.height = new_height
        self.rect.center = self.base_rect.center

        if self.hovered:
            glow = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (180, 180, 250, 60), glow.get_rect())
            surface.blit(glow, (self.rect.x - 10, self.rect.y - 10))

        color = self.current_color
        if self.hovered:
            brightness = 10 + int(15 * math.sin(pygame.time.get_ticks() * 0.005))
            color = (
                min(self.hover_color[0] + brightness, 255),
                min(self.hover_color[1] + brightness, 255),
                min(self.hover_color[2] + brightness, 255),
            )
        if self.clicked:
            color = self.click_color

        pygame.draw.rect(surface, color, self.rect, border_radius=16)
        if self.hovered:
            pygame.draw.rect(surface, (200, 200, 200, 100), self.rect, 3, border_radius=16)
            for _ in range(3):
                px = random.randint(self.rect.left, self.rect.right)
                py = random.randint(self.rect.top, self.rect.bottom)
                pygame.draw.circle(surface, (240, 240, 255), (px, py), 1)

        text_surf = self.font.render(self.text, True, BLACK if self.clicked else WHITE)
        surface.blit(
            text_surf,
            (self.rect.centerx - text_surf.get_width() // 2, self.rect.centery - text_surf.get_height() // 2)
        )
