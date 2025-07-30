import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from menu import MainMenu
from character_select import CharacterSelectScreen
from level1 import LevelOneScreen  # usa el nuevo nivel 1 con enemigos

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
level1_screen = None
selected_character_sprite = None

# ---- NUEVOS ESTADOS ----
state = "MENU"  # otros: "NIVEL1", "NIVEL1_COMPLETE", "NIVEL1_FAILED", "NIVEL2"
blink_timer = 0
show_press_space = True
font = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 30)


def draw_text(text, y):
    label = font.render(text, True, (255, 255, 255))
    rect = label.get_rect(center=(WIDTH//2, y))
    screen.blit(label, rect)

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
                    # --- INICIO DEL NIVEL 1 CON PERSONAJE SELECCIONADO ---
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

        elif state == "NIVEL1_FAILED":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reintentar
                    state = "NIVEL1"
                    level1_screen = LevelOneScreen(screen, selected_character_sprite)
                elif event.key == pygame.K_q:  # Salir
                    pygame.quit()
                    sys.exit()

        elif state == "NIVEL1_COMPLETE":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:  # Ir al siguiente nivel
                    state = "NIVEL2"  # aquí puedes cargar tu LevelTwoScreen
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    # ---- ACTUALIZAR Y DIBUJAR ----
    if state == "MENU":
        menu.update()
        menu.draw()

    elif state == "PERSONAJES":
        personajes_screen.update()
        personajes_screen.draw()

    elif state == "NIVEL1" and level1_screen:
        level1_screen.update()
        level1_screen.draw()
        # ---- CHEQUEAR RESULTADO DEL NIVEL ----
        if level1_screen.level_result == "WIN":
            state = "NIVEL1_COMPLETE"
        elif level1_screen.level_result == "LOSE":
            state = "NIVEL1_FAILED"

    elif state == "NIVEL1_FAILED":
        screen.fill((0, 0, 0))
        draw_text("¡Perdiste el nivel!", 200)
        draw_text("Presiona R para reintentar o Q para salir", 300)

    elif state == "NIVEL1_COMPLETE":
        screen.fill((0, 0, 0))
        draw_text("¡Nivel 1 completado!", 200)
        draw_text("Presiona N para ir al Nivel 2 o Q para salir", 300)

    elif state == "NIVEL2":
        screen.fill((0, 0, 0))
        draw_text("Nivel 2 (en construcción)", 200)
        draw_text("Presiona Q para salir", 300)

    pygame.display.flip()
    clock.tick(FPS)
