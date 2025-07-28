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

class Enemy:
    def __init__(self):
        self.walk_frames = self.load_frames("assetts/images/enemies/Minotaur_1/Walk.png", 64, 64, scale=1.0)
        self.attack_frames = self.load_frames("assetts/images/enemies/Minotaur_1/Attack.png", 64, 64, scale=1.0)

        self.rect = self.walk_frames[0].get_rect(midbottom=(WIDTH - 100, GROUND_Y))
        self.index = 0
        self.attacking = False
        self.alive = True
        self.attack_done = False

    def load_frames(self, path, fw, fh, scale=1):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        for y in range(0, sheet_height, fh):
            for x in range(0, sheet_width, fw):
                frame = sheet.subsurface((x, y, fw, fh))
                frames.append(pygame.transform.scale(frame, (int(fw*scale), int(fh*scale))))
        return frames

    def update(self, player_rect):
        if not self.alive:
            return

        if not self.attacking:
            if self.rect.x > player_rect.x + 50:
                self.rect.x -= 3
            else:
                self.attacking = True
                self.index = 0

        self.index += 0.2
        if self.attacking and self.index >= len(self.attack_frames):
            self.attack_done = True
            self.index = len(self.attack_frames)-1
        elif not self.attacking and self.index >= len(self.walk_frames):
            self.index = 0

    def draw(self, screen):
        if not self.alive:
            return
        if self.attacking:
            frame = self.attack_frames[int(self.index)]
        else:
            frame = self.walk_frames[int(self.index)]
        screen.blit(frame, self.rect)

class LevelOneScreen:
    def __init__(self, screen, player_sprite):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.background_frames = []
        bg_path = "assetts/images/level1/background"
        for file in sorted(os.listdir(bg_path)):
            if file.endswith(".png"):
                img = pygame.image.load(os.path.join(bg_path, file)).convert_alpha()
                img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                self.background_frames.append(img)
        self.current_bg_frame = 0
        self.bg_frame_rate = 8
        self.bg_frame_counter = 0

        self.player_sprite = player_sprite
        self.player_sprite.frames = [
            pygame.transform.scale(frame, (80, 80)).convert_alpha()
            for frame in self.player_sprite.frames
        ]
        self.player_rect = self.player_sprite.frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1

        self.bullets = pygame.sprite.Group()
        self.shoot_sound = pygame.mixer.Sound("assetts/sounds/shoot.wav") if os.path.exists("assetts/sounds/shoot.wav") else None

        self.enemy = Enemy()

        self.fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.fog.fill((200, 200, 200, 50))
        self.fog_x = -WIDTH

        self.start_ticks = pygame.time.get_ticks()

        self.game_over = False
        self.level_completed = False
        self.font = pygame.font.Font(None, 80)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_jumping and not self.game_over:
                self.is_jumping = True
                self.jump_velocity = -15
            if event.key == pygame.K_r and (self.game_over or self.level_completed):
                self.__init__(self.screen, self.player_sprite)
            if event.key == pygame.K_z and not self.game_over:
                self.shoot()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
            self.shoot()

    def shoot(self):
        bullet = Bullet(self.player_rect.right, self.player_rect.centery)
        self.bullets.add(bullet)
        if self.shoot_sound:
            self.shoot_sound.play()

    def update(self):
        if self.game_over or self.level_completed:
            return

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

        self.bullets.update()

        self.enemy.update(self.player_rect)

        if self.enemy.alive:
            for bullet in self.bullets:
                if self.enemy.rect.colliderect(bullet.rect):
                    self.enemy.alive = False
                    bullet.kill()
            if self.enemy.rect.colliderect(self.player_rect) and self.enemy.attack_done:
                self.game_over = True

        self.fog_x += 1
        if self.fog_x >= 0:
            self.fog_x = 0
            self.game_over = True

        seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        if seconds >= 30 and not self.game_over:
            self.level_completed = True

        self.bg_frame_counter += 1
        if self.bg_frame_counter >= self.bg_frame_rate:
            self.current_bg_frame = (self.current_bg_frame + 1) % len(self.background_frames)
            self.bg_frame_counter = 0

    def draw(self):
        self.screen.blit(self.background_frames[self.current_bg_frame], (0, 0))
        self.bullets.draw(self.screen)
        self.enemy.draw(self.screen)
        current_frame = self.player_sprite.frames[self.player_sprite.current_frame]
        self.screen.blit(current_frame, self.player_rect)
        self.screen.blit(self.fog, (self.fog_x, 0))

        if self.game_over:
            text = self.font.render("GAME OVER", True, (180, 0, 0))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        elif self.level_completed:
            text = self.font.render("NIVEL COMPLETADO", True, (0, 180, 0))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))