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
        base_path = "assetts/images/enemies/Minotaur_1"
        self.walk_frames = self.load_frames(os.path.join(base_path, "Walk.png"), 64, 64, scale=1.2)
        self.attack_frames = self.load_frames(os.path.join(base_path, "Attack.png"), 64, 64, scale=1.2)
        self.dead_frames = self.load_frames(os.path.join(base_path, "Dead.png"), 64, 64, scale=1.2)

        self.rect = self.walk_frames[0].get_rect()
        self.index = 0
        self.attacking = False
        self.dying = False
        self.alive = True
        self.attack_done = False
        self.current_action = "Walk"
        self.max_health = 5
        self.health = self.max_health

    def load_frames(self, path, fw, fh, scale=1):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sw, sh = sheet.get_size()
        for y in range(0, sh, fh):
            for x in range(0, sw, fw):
                frame = sheet.subsurface((x, y, fw, fh))
                frame = pygame.transform.scale(frame, (int(fw*scale), int(fh*scale)))
                frames.append(frame)
        return frames

    def update(self, player_rect):
        if not self.alive:
            return
        if self.dying:
            self.index += 0.2
            if self.index >= len(self.dead_frames):
                self.alive = False
            return
        if self.current_action == "Walk":
            if abs(self.rect.centerx - player_rect.centerx) < 200:
                self.attacking = True
                self.index = 0
            else:
                if self.rect.x > player_rect.x + 50:
                    self.rect.x -= 3
        self.index += 0.2
        if self.attacking:
            if self.index >= len(self.attack_frames):
                self.attack_done = True
                self.index = len(self.attack_frames) - 1
        else:
            if self.index >= len(self.walk_frames):
                self.index = 0

    def draw(self, screen):
        if not self.alive:
            return
        if self.dying:
            frame = self.dead_frames[int(self.index)]
        elif self.attacking:
            frame = self.attack_frames[int(self.index)]
        else:
            frame = self.walk_frames[int(self.index)]
        screen.blit(frame, self.rect)
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
            pygame.transform.scale(f, (100, 100)).convert_alpha()
            for f in self.player_sprite.frames
        ]
        self.player_rect = self.player_sprite.frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1
        self.bullets = pygame.sprite.Group()
        snd_path = "assetts/sounds/shoot.wav"
        self.shoot_sound = pygame.mixer.Sound(snd_path) if os.path.exists(snd_path) else None
        self.enemy = Enemy()
        self.enemy.rect.midbottom = (WIDTH + 400, GROUND_Y)
        self.game_over = False
        self.level_completed = False
        self.font = pygame.font.Font(None, 80)
        self.scroll_speed = 3

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
        b = Bullet(self.player_rect.right, self.player_rect.centery)
        self.bullets.add(b)
        if self.shoot_sound:
            self.shoot_sound.play()

    def update(self):
        if self.game_over:
            return None
        if self.level_completed:
            return "NEXT_LEVEL"
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player_rect.left > 0:
            self.player_rect.x -= self.player_speed
        if keys[pygame.K_d]:
            if self.player_rect.x < WIDTH / 3:
                self.player_rect.x += self.player_speed
            else:
                self.enemy.rect.x -= self.scroll_speed
                for bullet in self.bullets:
                    bullet.rect.x -= self.scroll_speed
        if self.is_jumping:
            self.player_rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            if self.player_rect.bottom >= GROUND_Y:
                self.player_rect.bottom = GROUND_Y
                self.is_jumping = False
        self.player_sprite.update()
        self.bullets.update()
        if self.enemy.rect.x > WIDTH - self.enemy.rect.width - 50:
            self.enemy.rect.x -= 2
            self.enemy.current_action = "Walk"
        else:
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
                elif self.enemy.attack_done:
                    self.game_over = True
        if not self.enemy.alive:
            self.level_completed = True
        self.bg_frame_counter += 1
        if self.bg_frame_counter >= self.bg_frame_rate:
            self.current_bg_frame = (self.current_bg_frame + 1) % len(self.background_frames)
            self.bg_frame_counter = 0
        return None

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_frames[self.current_bg_frame], (0, 0))
        self.bullets.draw(self.screen)
        self.enemy.draw(self.screen)
        frame = self.player_sprite.frames[self.player_sprite.current_frame]
        self.screen.blit(frame, self.player_rect)
        if self.game_over:
            msg = self.font.render("GAME OVER", True, (180, 0, 0))
            self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
            retry_msg = pygame.font.Font(None, 40).render("Presiona 'R' para Reintentar", True, (255, 255, 255))
            self.screen.blit(retry_msg, (WIDTH//2 - retry_msg.get_width()//2, HEIGHT//2 + 80))
        elif self.level_completed:
            fancy_font = pygame.font.Font("assetts/fonts/PressStart2P-Regular.ttf", 60)
            msg = fancy_font.render("NIVEL COMPLETADO", True, (0, 255, 0))
            self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
