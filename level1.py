import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from menu import MainMenu
from character_select import CharacterSelectScreen
from level1 import LevelOneScreen

pygame.init()

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
level1_screen = None
selected_character_sprite = None

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
                if selected_character_sprite:
                    state = "NIVEL1"
                    level1_screen = LevelOneScreen(screen, selected_character_sprite)

        elif state == "PERSONAJES":
            personajes_screen.handle_event(event)

            if personajes_screen.selected_index is not None:
                selected_character = personajes_screen.characters[personajes_screen.selected_index]
                selected_character_sprite = selected_character["sprite"]
                print("Seleccionaste el personaje:", selected_character["name"])

            if personajes_screen.btn_volver.clicked:
                state = "MENU"
                personajes_screen.btn_volver.clicked = False

        elif state == "NIVEL1" and level1_screen:
            level1_screen.handle_event(event)

    if state == "MENU":
        menu.update()
        menu.draw()
    elif state == "PERSONAJES":
        personajes_screen.update()
        personajes_screen.draw()
    elif state == "NIVEL1" and level1_screen:
        level1_screen.update()
        level1_screen.draw()

    pygame.display.flip()
    clock.tick(FPS)