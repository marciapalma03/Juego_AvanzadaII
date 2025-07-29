import pygame
import os
from background import Background
from button import StoneButton
from settings import WIDTH, HEIGHT
from character_sprite import CharacterSprite

TARGET_SIZE = (400, 400)  # Tamaño estándar para todos los sprites

# -------- BOTÓN POPUP ESTILO PIEDRA ---------
class PopupButton:
    def __init__(self, text, pos, size, sound_hover, sound_click):
        self.text = text
        self.base_rect = pygame.Rect(pos, size)
        self.rect = self.base_rect.copy()
        self.sound_hover = sound_hover
        self.sound_click = sound_click
        self.font = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 22)
        self.base_color = (220, 220, 160)
        self.edge_color = (130, 130, 90)
        self.text_color = (0, 0, 0)
        self.hovered = False
        self.clicked = False
        self.grow_scale = 1.12
        self.played_hover = False

    def draw(self, screen):
        rect = self.rect
        pygame.draw.rect(screen, self.base_color, rect, border_radius=12)
        pygame.draw.rect(screen, self.edge_color, rect, 3, border_radius=12)
        text_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(
            text_surf,
            (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2),
        )

    def update(self, mouse_pos):
        if self.base_rect.collidepoint(mouse_pos):
            if not self.hovered:
                self.rect = self.base_rect.inflate(
                    self.base_rect.width * (self.grow_scale - 1),
                    self.base_rect.height * (self.grow_scale - 1),
                )
                self.hovered = True
                if not self.played_hover:
                    self.sound_hover.play()
                    self.played_hover = True
            else:
                self.rect = self.rect
        else:
            if self.hovered:
                self.rect = self.base_rect.copy()
                self.played_hover = False
            self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.sound_click.play()
            self.clicked = True

# ------------ SELECCIÓN DE PERSONAJES -----------
class CharacterSelectScreen:
    def __init__(self, screen):
        self.screen = screen
        self.bg = Background("assetts/images/backgrounds/frames/", fps=10)
        self.blur_scale = 0.18

        click_sound = pygame.mixer.Sound(os.path.join("assetts/sounds/click.mp3"))
        hover_sound = pygame.mixer.Sound(os.path.join("assetts/sounds/hover.mp3"))
        margin = 40
        btn_width, btn_height = 250, 75
        self.btn_volver = StoneButton("VOLVER", (margin, HEIGHT - btn_height - margin), (btn_width, btn_height), click_sound)

        self.characters = [
            {
                "name": "YAMATO",
                "sprite": CharacterSprite("assetts/images/characters/yamato/idle.png", 200, 200, 4, fps=8, scale=4),
            },
            {
                "name": "KIZAME",
                "sprite": CharacterSprite("assetts/images/characters/kizame/idle.png", 100, 100, 10, fps=8, scale=4),
            },
            {
                "name": "RIN",
                "sprite": CharacterSprite("assetts/images/characters/rin/idle.png", 150, 150, 8, fps=8, scale=4),
            },
        ]
        self.descriptions = [
            "Guerrero equilibrado con alta defensa y ataque cuerpo a cuerpo.",
            "Arquero ágil, ataques a distancia y gran velocidad.",
            "Maga con hechizos de área, defensa baja pero gran daño."
        ]

        sprites = [char["sprite"] for char in self.characters]
        self.char_positions = self.calculate_positions_horizontal_centered(TARGET_SIZE, len(sprites), HEIGHT // 2 - 60, WIDTH, separation=-70)

        self.selected_index = None
        self.hover_index = None

        # Botones del popup
        self.popup_hover_sound = hover_sound
        self.popup_click_sound = click_sound
        self.close_btn = None
        self.select_btn = None

        # -------- NUEVO: para guardar el personaje elegido --------
        self.selected_character = None

    def calculate_positions_horizontal_centered(self, size, num_sprites, y_center, screen_width, separation=-70):
        w, h = size
        total_width = num_sprites * w + (num_sprites - 1) * separation
        start_x = (screen_width - total_width) // 2
        positions = []
        for i in range(num_sprites):
            x = start_x + i * (w + separation)
            y = y_center - h // 2
            positions.append((x, y))
        return positions

    def update(self):
        self.bg.update()
        mouse_pos = pygame.mouse.get_pos()
        self.btn_volver.update(mouse_pos)
        self.hover_index = None
        for idx, char in enumerate(self.characters):
            char["sprite"].update()
            x, y = self.char_positions[idx]
            rect = pygame.Rect(x, y, *TARGET_SIZE)
            if rect.collidepoint(mouse_pos):
                self.hover_index = idx

        # Popup buttons
        if self.selected_index is not None:
            box_w, box_h = 560, 340
            box_x, box_y = WIDTH // 2 - box_w // 2, HEIGHT // 2 - box_h // 2
            btn_w, btn_h = 120, 36
            select_w = 170
            btn_margin = 24
            close_btn_pos = (box_x + btn_margin, box_y + box_h - btn_h - btn_margin)
            select_btn_pos = (box_x + box_w - select_w - btn_margin, box_y + box_h - btn_h - btn_margin)
            if not self.close_btn or not self.select_btn:
                self.close_btn = PopupButton("CERRAR", close_btn_pos, (btn_w, btn_h), self.popup_hover_sound, self.popup_click_sound)
                self.select_btn = PopupButton("SELECCIONAR", select_btn_pos, (select_w, btn_h), self.popup_hover_sound, self.popup_click_sound)
            else:
                self.close_btn.base_rect.topleft = close_btn_pos
                self.close_btn.rect = self.close_btn.base_rect.copy()
                self.select_btn.base_rect.topleft = select_btn_pos
                self.select_btn.rect = self.select_btn.base_rect.copy()
            self.close_btn.update(mouse_pos)
            self.select_btn.update(mouse_pos)

    def handle_event(self, event):
        self.btn_volver.handle_event(event)
        if self.selected_index is not None:
            self.close_btn.handle_event(event)
            self.select_btn.handle_event(event)
            if self.close_btn.clicked:
                self.selected_index = None
                self.close_btn.clicked = False
            elif self.select_btn.clicked:
                print("Seleccionaste el personaje:", self.characters[self.selected_index]["name"])
                # -------- NUEVO: guardar personaje elegido --------
                self.selected_character = self.characters[self.selected_index]["name"]
                self.selected_index = None
                self.select_btn.clicked = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover_index is not None:
                self.selected_index = self.hover_index

    def draw(self):
        frame = self.bg.frames[self.bg.current_frame]
        small_w, small_h = int(WIDTH * self.blur_scale), int(HEIGHT * self.blur_scale)
        blur = pygame.transform.smoothscale(frame, (small_w, small_h))
        blur = pygame.transform.smoothscale(blur, (WIDTH, HEIGHT))
        self.screen.blit(blur, (0, 0))

        font = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 48)
        txt = font.render("SELECCION DE PERSONAJE", True, (255, 255, 230))
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 80))

        for idx, char in enumerate(self.characters):
            x, y = self.char_positions[idx]
            current_frame = char["sprite"].frames[char["sprite"].current_frame]
            scaled_sprite = pygame.transform.smoothscale(current_frame, TARGET_SIZE)
            self.screen.blit(scaled_sprite, (x, y))

        self.btn_volver.draw(self.screen)

        if self.selected_index is not None:
            self.draw_character_popup(self.selected_index)

    def draw_character_popup(self, idx):
        # Fondo transparente
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        # Recuadro
        box_w, box_h = 560, 340
        box_x, box_y = WIDTH // 2 - box_w // 2, HEIGHT // 2 - box_h // 2
        pygame.draw.rect(self.screen, (40, 40, 60), (box_x, box_y, box_w, box_h), border_radius=30)
        pygame.draw.rect(self.screen, (200, 200, 255), (box_x, box_y, box_w, box_h), 4, border_radius=30)
        # Sprite del personaje
        sprite = self.characters[idx]["sprite"].frames[0]
        sprite_big = pygame.transform.smoothscale(sprite, (110, 110))
        self.screen.blit(sprite_big, (box_x + 40, box_y + 80))
        # Nombre y descripción
        font_title = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 38)
        font_desc = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 19)
        name_surface = font_title.render(self.characters[idx]["name"], True, (255, 255, 220))
        self.screen.blit(name_surface, (box_x + 200, box_y + 60))
        desc = self.descriptions[idx]
        max_width = box_w - 220 - 30
        words = desc.split()
        lines, temp = [], ""
        for word in words:
            test_line = (temp + " " + word).strip()
            if font_desc.size(test_line)[0] > max_width:
                lines.append(temp)
                temp = word
            else:
                temp = test_line
        if temp:
            lines.append(temp)
        for i, line in enumerate(lines):
            line_surface = font_desc.render(line, True, (255, 255, 220))
            self.screen.blit(line_surface, (box_x + 200, box_y + 110 + i * 27))
        # Botones
        self.close_btn.draw(self.screen)
        self.select_btn.draw(self.screen)
