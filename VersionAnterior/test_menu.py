import pygame
import sys

WIDTH, HEIGHT = 900, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colores
GRAY = (100, 100, 100)
BLUE = (100, 160, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fuentes
font = pygame.font.SysFont("arialblack", 36)

state = "MENU"

# Define rects para los botones
btn_personajes = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 80)
btn_volver = pygame.Rect(WIDTH//2 - 150, HEIGHT - 120, 300, 80)

def draw_menu():
    screen.fill(GRAY)
    text = font.render("MENU PRINCIPAL", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 120))
    pygame.draw.rect(screen, BLUE, btn_personajes, border_radius=18)
    label = font.render("PERSONAJES", True, BLACK)
    screen.blit(label, (btn_personajes.centerx - label.get_width()//2, btn_personajes.centery - label.get_height()//2))

def draw_personajes():
    screen.fill((40, 50, 60))
    text = font.render("SELECCIÓN DE PERSONAJE", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 120))
    pygame.draw.rect(screen, (200,120,120), btn_volver, border_radius=18)
    label = font.render("VOLVER", True, BLACK)
    screen.blit(label, (btn_volver.centerx - label.get_width()//2, btn_volver.centery - label.get_height()//2))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "MENU" and btn_personajes.collidepoint(event.pos):
                state = "PERSONAJES"
            elif state == "PERSONAJES" and btn_volver.collidepoint(event.pos):
                state = "MENU"

    if state == "MENU":
        draw_menu()
    elif state == "PERSONAJES":
        draw_personajes()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
