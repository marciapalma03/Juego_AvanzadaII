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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        base_path = "assets/images/enemies/enemie_1/"
        self.walk_frames = self.load_frames(os.path.join(base_path, "Walk.png"), 64, 64, scale=2.0)
        self.attack_frames = self.load_frames(os.path.join(base_path, "Attack_1.png"), 64, 64, scale=2.0)
        self.dead_frames = self.load_frames(os.path.join(base_path, "Dead.png"), 64, 64, scale=2.0)
        self.rect = self.walk_frames[0].get_rect(midbottom=(x, y))
        self.index = 0
        self.attacking = False
        self.dying = False
        self.alive = True
        self.health = 5
        self.max_health = 5

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
                self.index = len(self.dead_frames) - 1
                self.alive = False
            return
        if self.rect.x > player_rect.x + 50:
            self.rect.x -= 3
        self.attacking = abs(self.rect.centerx - player_rect.centerx) < 200
        self.index += 0.2
        if self.attacking and self.index >= len(self.attack_frames):
            self.index = 0
        elif not self.attacking and self.index >= len(self.walk_frames):
            self.index = 0

    def draw(self, screen):
        if not self.alive:
            return
        if self.dying:
            frame = self.dead_frames[min(int(self.index), len(self.dead_frames) - 1)]
        elif self.attacking:
            frame = self.attack_frames[int(self.index) % len(self.attack_frames)]
        else:
            frame = self.walk_frames[int(self.index) % len(self.walk_frames)]
        screen.blit(frame, self.rect)
        if not self.dying:
            bar_w = self.rect.width
            ratio = self.health / self.max_health
            bg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_w, 6)
            fg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, int(bar_w * ratio), 6)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            pygame.draw.rect(screen, (200, 0, 0), fg_rect)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        image_path = "assets/images/icons/obstacles/Jump_Bonus_02.png"
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))

    def update(self):
        self.rect.x -= 2
        if self.rect.right < 0:
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

class LevelTwoScreen:
    def __init__(self, screen, player_sprite):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.background_image = pygame.image.load("assets/images/level2/Cartoon_Forest_BG_01.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))
        self.original_frames = player_sprite.frames
        self.player_frames = [pygame.transform.scale(f, (150, 150)).convert_alpha() for f in self.original_frames]
        self.player_sprite = player_sprite
        self.player_rect = self.player_frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        for i in range(3):
            enemy = Enemy(WIDTH + i * 200, GROUND_Y)
            self.enemies.add(enemy)
        for i in range(3):
            obstacle = Obstacle(WIDTH + i * 300)
            self.obstacles.add(obstacle)
        self.goal = Goal(WIDTH - 50)

        font_path = "assets/fonts/PressStart2P-Regular.ttf"
        self.font = pygame.font.Font(font_path, 60)
        self.small_font = pygame.font.Font(font_path, 30)
        self.completed = False
        self.completed_timer = 0
        self.game_over = False

    def handle_event(self, event):
        if self.game_over or self.completed:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RETRY"
                elif event.key == pygame.K_m:
                    return "MENU"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_jumping and not self.game_over:
                self.is_jumping = True
                self.jump_velocity = -15
            if event.key == pygame.K_z and not self.game_over:
                self.shoot()
        return None

    def shoot(self):
        bullet = Bullet(self.player_rect.right, self.player_rect.centery)
        self.bullets.add(bullet)

    def update(self):
        if self.completed:
            self.completed_timer += 1
            if self.completed_timer >= 180:  # 3 segundos (60 FPS)
                return "NEXT_LEVEL"
            return None

        if self.game_over:
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
        for enemy in self.enemies:
            enemy.update(self.player_rect)
        self.obstacles.update()

        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                bullet.kill()
                enemy.health -= 1
                if enemy.health <= 0:
                    enemy.dying = True
                    enemy.index = 0

        for enemy in self.enemies:
            if enemy.alive and not enemy.dying and self.player_rect.colliderect(enemy.rect):
                self.game_over = True
                break

        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle.rect):
                self.player_rect.x -= 10

        if self.player_rect.colliderect(self.goal.rect) and all(not e.alive for e in self.enemies):
            self.completed = True
            self.completed_timer = 0
        return None

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_image, (0, 0))
        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image, obstacle.rect)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.bullets.draw(self.screen)
        self.screen.blit(self.goal.image, self.goal.rect)
        frame = self.player_frames[self.player_sprite.current_frame]
        self.screen.blit(frame, self.player_rect)

        if self.completed:
            msg = self.font.render("NIVEL COMPLETADO", True, (0, 255, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        elif self.game_over:
            msg = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
            retry_msg = self.small_font.render("Presiona 'R' para Reintentar", True, (255, 255, 255))
            menu_msg = self.small_font.render("Presiona 'M' para volver al menú", True, (255, 255, 255))
            self.screen.blit(retry_msg, (WIDTH // 2 - retry_msg.get_width() // 2, HEIGHT // 2 + 80))
            self.screen.blit(menu_msg, (WIDTH // 2 - menu_msg.get_width() // 2, HEIGHT // 2 + 120))
