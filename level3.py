import pygame
import os
import random
from settings import WIDTH, HEIGHT

GROUND_Y = HEIGHT - 100

# ===========================
# CLASES DE APOYO
# ===========================
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
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 2
        self.health = 3

    def update(self):
        self.rect.x -= self.speed

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))

    def update(self):
        self.rect.x -= 2
        if self.rect.right < 0:
            self.kill()

# ===========================
# JEFE FINAL (MINOTAUR_3)
# ===========================
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((120, 120))
        self.image.fill((50, 0, 200))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.health = 20
        self.attack_timer = 0
        self.attack_delay = 60  # cada 1 segundo
        self.dead = False

    def update(self):
        self.attack_timer += 1

    def shoot(self, bullets_group):
        if self.attack_timer >= self.attack_delay:
            bullet = BossBullet(self.rect.left, self.rect.centery)
            bullets_group.add(bullet)
            self.attack_timer = 0

# ===========================
# PANTALLA DEL NIVEL 3
# ===========================
class LevelThreeScreen:
    def __init__(self, screen, player_sprite):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # --- FONDO ESTÁTICO ---
        self.background_image = pygame.image.load("assets/images/level3/Cartoon_Forest_BG_02.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

        # Jugador (frames copiados y escalados, sin alterar los originales)
        self.player_sprite = player_sprite
        self.player_frames = [
            pygame.transform.scale(f, (80, 80)).convert_alpha()
            for f in player_sprite.frames
        ]
        self.player_rect = self.player_frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1

        # Entidades
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()

        for i in range(5):
            enemy = Enemy(WIDTH + i * 250, GROUND_Y)
            self.enemies.add(enemy)
        for i in range(4):
            obstacle = Obstacle(WIDTH + i * 300)
            self.obstacles.add(obstacle)

        # Jefe final
        self.boss = Boss(WIDTH - 150, GROUND_Y)
        self.font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 40)
        self.completed = False
        self.game_over = False

    def handle_event(self, event):
        if self.game_over:  # --- manejo de teclas cuando se pierde
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RETRY"
                elif event.key == pygame.K_m:
                    return "MENU"
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.is_jumping:
                    self.is_jumping = True
                    self.jump_velocity = -15
                if event.key == pygame.K_z:
                    self.shoot()
        return None

    def shoot(self):
        bullet = Bullet(self.player_rect.right, self.player_rect.centery)
        self.bullets.add(bullet)

    def update(self):
        if self.completed or self.game_over:
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
        self.enemies.update()
        self.obstacles.update()
        self.boss.update()
        self.boss_bullets.update()

        # Disparos del jefe
        self.boss.shoot(self.boss_bullets)

        # Colisiones
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                bullet.kill()
                enemy.health -= 1
                if enemy.health <= 0:
                    enemy.kill()
            if self.boss.rect.colliderect(bullet.rect) and not self.boss.dead:
                bullet.kill()
                self.boss.health -= 1
                if self.boss.health <= 0:
                    self.boss.dead = True
                    self.completed = True

        if pygame.sprite.spritecollideany(self.player_rect_to_sprite(), self.enemies):
            self.game_over = True

        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle.rect):
                self.player_rect.x -= 10

        for bullet in self.boss_bullets:
            if self.player_rect.colliderect(bullet.rect):
                self.game_over = True

        return None

    def player_rect_to_sprite(self):
        temp = pygame.sprite.Sprite()
        temp.rect = self.player_rect
        return temp

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_image, (0, 0))  # --- FONDO ESTÁTICO ---
        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image, obstacle.rect)
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        self.bullets.draw(self.screen)
        self.boss_bullets.draw(self.screen)

        if not self.boss.dead:
            self.screen.blit(self.boss.image, self.boss.rect)

        frame = self.player_frames[self.player_sprite.current_frame]
        self.screen.blit(frame, self.player_rect)

        if self.completed:
            msg = self.font.render("¡JEFE DERROTADO!", True, (0, 255, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        elif self.game_over:
            msg = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
            retry_msg = self.small_font.render("Presiona 'R' para Reintentar o 'M' para Menu", True, (255, 255, 255))
            self.screen.blit(retry_msg, (WIDTH // 2 - retry_msg.get_width() // 2, HEIGHT // 2 + 60))
