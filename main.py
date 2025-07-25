import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from menu import MainMenu
from character_select import CharacterSelectScreen
from level1 import LevelOneScreen  # Importa la clase del nivel 1

pygame.init()

# ---- Música de fondo ----
pygame.mixer.init()
pygame.mixer.music.load("assetts/music/musicainicio.mp3")
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)
current_music = "menu"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mi Juego")
clock = pygame.time.Clock()

menu = MainMenu(screen)
personajes_screen = CharacterSelectScreen(screen)
level1_screen = LevelOneScreen(screen)  # Instancia la pantalla del nivel 1

state = "MENU"

blink_timer = 0
show_press_space = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if state == "MENU":
            menu.handle_event(event)
            if menu.btn_personajes.clicked:
                state = "PERSONAJES"
                pygame.mixer.music.set_volume(0.18)
                menu.btn_personajes.clicked = False
            if menu.btn_salir.clicked:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "NIVEL1"
                if current_music != "nivel1":
                    pygame.mixer.music.load("assetts/music/music_nivel1.mp3")  # Cambia a tu archivo real
                    pygame.mixer.music.set_volume(0.23)
                    pygame.mixer.music.play(-1)
                    current_music = "nivel1"
        elif state == "PERSONAJES":
            personajes_screen.handle_event(event)
            if personajes_screen.btn_volver.clicked:
                state = "MENU"
                if current_music != "menu":
                    pygame.mixer.music.load("assetts/music/musicainicio.mp3")
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play(-1)
                    current_music = "menu"
                personajes_screen.btn_volver.clicked = False
        elif state == "NIVEL1":
            level1_screen.handle_event(event)

    if state == "MENU":
        menu.update()
        menu.draw()
        blink_timer += clock.get_time()
        if blink_timer > 500:
            show_press_space = not show_press_space
            blink_timer = 0
        if show_press_space:
            font = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 20)
            txt = font.render("Presione ESPACIO para jugar", True, (255, 255, 160))
            y_pos = HEIGHT - 60
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y_pos))
    elif state == "PERSONAJES":
        personajes_screen.update()
        personajes_screen.draw()
    elif state == "NIVEL1":
        level1_screen.update()
        level1_screen.draw()

    pygame.display.flip()
    clock.tick(FPS)
