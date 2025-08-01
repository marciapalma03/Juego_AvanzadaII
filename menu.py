import pygame
import os
from button import StoneButton
from background import Background
from settings import WIDTH, HEIGHT

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.bg = Background("assets/images/backgrounds/frames/", fps=10)

        # Fuentes para el título
        font_path = "assets/fonts/PressStart2P-Regular.ttf"
        self.title_font = pygame.font.Font(font_path, 80)
        self.mist_font = pygame.font.Font(font_path, 160)

        # Sonido de click
        click_sound = pygame.mixer.Sound(os.path.join("assets/sounds/clicks.mp3"))

        margin = 40
        btn_width, btn_height = 340, 75
        # Botón PERSONAJES (esquina inferior derecha)
        self.btn_personajes = StoneButton(
            "PERSONAJES",
            (WIDTH - btn_width - margin, HEIGHT - btn_height - margin),
            (btn_width, btn_height),
            click_sound
        )
        # Botón SALIR (esquina inferior izquierda)
        self.btn_salir = StoneButton(
            "SALIR",
            (margin, HEIGHT - btn_height - margin),
            (btn_width, btn_height),
            click_sound
        )
        self.buttons = [self.btn_personajes, self.btn_salir]

    def draw(self):
        self.bg.draw(self.screen)
        x = 60
        y = 80

        # Línea 1: THE
        the_surface = self.title_font.render("THE", True, (255, 255, 255))
        self.screen.blit(the_surface, (x, y))
        y += self.title_font.get_height() + 40

        # Línea 2: LEGACY y MIST al lado
        legacy_surface = self.title_font.render("LEGACY", True, (255, 255, 255))
        mist_surface = self.mist_font.render("MIST", True, (255, 255, 200))
        # LEGACY a la izquierda
        self.screen.blit(legacy_surface, (x, y))
        # MIST grande a la derecha de LEGACY (ajusta +60 para separación horizontal)
        mist_x = x + legacy_surface.get_width() + 60
        mist_y = y - (mist_surface.get_height() - legacy_surface.get_height()) // 2  # Centrado vertical
        self.screen.blit(mist_surface, (mist_x, mist_y))
        y += self.title_font.get_height() + 40

        # Línea 3: OF THE
        ofthe_surface = self.title_font.render("OF THE", True, (255, 255, 255))
        self.screen.blit(ofthe_surface, (x, y))

        # Dibuja botones
        for btn in self.buttons:
            btn.draw(self.screen)

    def update(self):
        self.bg.update()
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
