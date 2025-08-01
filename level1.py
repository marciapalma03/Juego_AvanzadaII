import pygame
import os
from settings import WIDTH, HEIGHT

GROUND_Y = HEIGHT - 100

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.kill()

class Goal(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        image_path = os.path.join("assets/images/icons/final/50.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        mask = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
        self.image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))

class Enemy:
    def __init__(self):
        base_path = "assets/images/enemies/enemie_1/"
        self.walk_frames = self.load_frames(os.path.join(base_path, "Walk.png"), 64, 64, scale=2.0)
        self.attack_frames = self.load_frames(os.path.join(base_path, "Attack_1.png"), 64, 64, scale=2.0)
        self.dead_frames = self.load_frames(os.path.join(base_path, "Dead.png"), 64, 64, scale=2.0)

        self.index = 0
        self.attacking = False
        self.dying = False
        self.alive = True
        self.max_health = 5
        self.health = self.max_health
        self.rect = self.walk_frames[0].get_rect(midbottom=(WIDTH - 200, GROUND_Y))
        self.current_frame = self.walk_frames[0]

    def load_frames(self, path, fw, fh, scale=1):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sw, sh = sheet.get_size()
        for y in range(0, sh, fh):
            for x in range(0, sw, fw):
                frame = sheet.subsurface((x, y, fw, fh))
                frame = pygame.transform.scale(frame, (int(fw * scale), int(fh * scale)))
                frames.append(frame)
        return frames

    def update(self, player_rect):
        if not self.alive:
            return

        if self.dying:
            self.index += 0.15
            if self.index >= len(self.dead_frames):
                self.alive = False
            else:
                self.current_frame = self.dead_frames[int(self.index)]
            return

        if self.rect.x > player_rect.x + 50:
            self.rect.x -= 3

        self.attacking = abs(self.rect.centerx - player_rect.centerx) < 200
        self.index += 0.2
        if self.attacking:
            self.current_frame = self.attack_frames[int(self.index) % len(self.attack_frames)]
        else:
            self.current_frame = self.walk_frames[int(self.index) % len(self.walk_frames)]

    def draw(self, screen):
        if not self.alive:
            return
        screen.blit(self.current_frame, self.rect)
        if not self.dying:
            bar_w = self.rect.width
            ratio = self.health / self.max_health
            bg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_w, 6)
            fg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, int(bar_w * ratio), 6)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            pygame.draw.rect(screen, (200, 0, 0), fg_rect)

class LevelOneScreen:
    def __init__(self, screen, player_sprite):
        self.screen = screen
        self.clock = pygame.time.Clock()

        bg_path = "assets/images/level1/Cartoon_Forest_BG_03.png"
        self.background = pygame.image.load(bg_path).convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.player_sprite = player_sprite
        self.player_frames = [
            pygame.transform.scale(f, (150, 150)).convert_alpha()
            for f in player_sprite.frames
        ]
        self.player_rect = self.player_frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1
        self.bullets = pygame.sprite.Group()
        snd_path = "assets/sounds/shoot.wav"
        self.shoot_sound = pygame.mixer.Sound(snd_path) if os.path.exists(snd_path) else None
        self.enemy = Enemy()
        self.goal = Goal(WIDTH - 50)
        self.game_over = False
        self.level_completed = False

        # === FUENTE PERSONALIZADA ===
        font_path = "assets/fonts/PressStart2P-Regular.ttf"
        self.font = pygame.font.Font(font_path, 60)
        self.small_font = pygame.font.Font(font_path, 30)

        # === NUEVO: temporizador para la transición ===
        self.completed_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_jumping and not self.game_over:
                self.is_jumping = True
                self.jump_velocity = -15
            if event.key == pygame.K_r and (self.game_over or self.level_completed):
                self.__init__(self.screen, self.player_sprite)
            if event.key == pygame.K_m and (self.game_over or self.level_completed):
                return "MENU"
            if event.key == pygame.K_z and not self.game_over:
                self.shoot()

    def shoot(self):
        b = Bullet(self.player_rect.right, self.player_rect.centery)
        self.bullets.add(b)
        if self.shoot_sound:
            self.shoot_sound.play()

    def update(self):
        if self.game_over:
            return None

        # Si el nivel ya está completado, aumentar contador y esperar 3 segundos (180 frames a 60FPS)
        if self.level_completed:
            self.completed_timer += 1
            if self.completed_timer > 180:
                return "NEXT_LEVEL"
            return None

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player_rect.left > 0:
            self.player_rect.x -= self.player_speed
        if keys[pygame.K_d] and self.player_rect.right < WIDTH:
            self.player_rect.x += self.player_speed

        if self.is_jumping:
            self.player_rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            if self.player_rect.bottom >= GROUND_Y:
                self.player_rect.bottom = GROUND_Y
                self.is_jumping = False

        self.player_sprite.update()
        self.bullets.update()
        self.enemy.update(self.player_rect)

        if self.enemy.alive and not self.enemy.dying:
            for b in self.bullets:
                if self.enemy.rect.colliderect(b.rect):
                    b.kill()
                    self.enemy.health -= 1
                    if self.enemy.health <= 0:
                        self.enemy.dying = True
                        self.enemy.index = 0

        if self.enemy.alive and not self.enemy.dying:
            if self.player_rect.colliderect(self.enemy.rect):
                if self.player_rect.bottom <= self.enemy.rect.top + 10 and self.jump_velocity > 0:
                    self.is_jumping = True
                    self.jump_velocity = -12
                else:
                    if self.enemy.attacking:
                        self.game_over = True

        if not self.enemy.alive and self.player_rect.colliderect(self.goal.rect):
            self.level_completed = True
            self.completed_timer = 0
        return None

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))
        self.bullets.draw(self.screen)
        self.enemy.draw(self.screen)
        self.screen.blit(self.goal.image, self.goal.rect)
        frame = self.player_frames[self.player_sprite.current_frame]
        self.screen.blit(frame, self.player_rect)

        if self.game_over:
            msg = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
            retry_msg = self.small_font.render("Presiona 'R' para Reintentar", True, (255, 255, 255))
            menu_msg = self.small_font.render("Presiona 'M' para volver al menú", True, (255, 255, 255))
            self.screen.blit(retry_msg, (WIDTH // 2 - retry_msg.get_width() // 2, HEIGHT // 2 + 80))
            self.screen.blit(menu_msg, (WIDTH // 2 - menu_msg.get_width() // 2, HEIGHT // 2 + 120))
        elif self.level_completed:
            msg = self.font.render("NIVEL COMPLETADO", True, (0, 255, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 50))
