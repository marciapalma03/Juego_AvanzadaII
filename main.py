import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from menu import MainMenu
from character_select import CharacterSelectScreen
from level1 import LevelOneScreen
from level2 import LevelTwoScreen
from level3 import LevelThreeScreen  # Nivel 3

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/music/musicainicio.mp3")
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mi Juego")
clock = pygame.time.Clock()

menu = MainMenu(screen)
personajes_screen = CharacterSelectScreen(screen)
level1_screen = None
level2_screen = None
level3_screen = None
selected_character_sprite = None

state = "MENU"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ---- MENÚ PRINCIPAL ----
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

        # ---- PANTALLA DE SELECCIÓN ----
        elif state == "PERSONAJES":
            personajes_screen.handle_event(event)
            if personajes_screen.selected_index is not None:
                selected_character = personajes_screen.characters[personajes_screen.selected_index]
                selected_character_sprite = selected_character["sprite"]
                print("Seleccionaste el personaje:", selected_character["name"])
            if personajes_screen.btn_volver.clicked:
                state = "MENU"
                personajes_screen.btn_volver.clicked = False

        # ---- NIVEL 1 ----
        elif state == "NIVEL1" and level1_screen:
            action = level1_screen.handle_event(event)
            if action == "RETRY":
                level1_screen = LevelOneScreen(screen, selected_character_sprite)
            elif action == "MENU":
                state = "MENU"

        # ---- NIVEL 2 ----
        elif state == "NIVEL2" and level2_screen:
            action = level2_screen.handle_event(event)
            if action == "RETRY":
                level2_screen = LevelTwoScreen(screen, selected_character_sprite)
            elif action == "MENU":
                state = "MENU"

        # ---- NIVEL 3 ----
        elif state == "NIVEL3" and level3_screen:
            action = level3_screen.handle_event(event)
            if action == "RETRY":
                level3_screen = LevelThreeScreen(screen, selected_character_sprite)
            elif action == "MENU":
                state = "MENU"

    # --- Dibujo y actualización de estados ---
    if state == "MENU":
        menu.update()
        menu.draw()

    elif state == "PERSONAJES":
        personajes_screen.update()
        personajes_screen.draw()

    elif state == "NIVEL1" and level1_screen:
        result = level1_screen.update()
        level1_screen.draw()
        if result == "NEXT_LEVEL":
            state = "NIVEL2"
            level2_screen = LevelTwoScreen(screen, selected_character_sprite)

    elif state == "NIVEL2" and level2_screen:
        result = level2_screen.update()
        level2_screen.draw()
        if result == "NEXT_LEVEL":
            state = "NIVEL3"
            level3_screen = LevelThreeScreen(screen, selected_character_sprite)

    elif state == "NIVEL3" and level3_screen:
        result = level3_screen.update()
        level3_screen.draw()
        # Si el nivel 3 termina con éxito podrías manejar transición final aquí
        # if getattr(level3_screen, "completed", False):
        #     state = "MENU"

    pygame.display.flip()
    clock.tick(FPS)
