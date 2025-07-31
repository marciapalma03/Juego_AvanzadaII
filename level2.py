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

class Goal(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface((40, 100))
        self.image.fill((0, 255, 0))  # Verde para identificarlo
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))

# --- Pantalla del nivel 2 ---
class LevelTwoScreen:
    def __init__(self, screen, player_sprite):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Fondo animado
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

        # Jugador
        self.player_sprite = player_sprite
        self.player_sprite.frames = [
            pygame.transform.scale(f, (80, 80)).convert_alpha()
            for f in self.player_sprite.frames
        ]
        self.player_rect = self.player_sprite.frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1

        # Entidades del nivel
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        for i in range(5):
            enemy = Enemy(WIDTH + i * 200, GROUND_Y)
            self.enemies.add(enemy)
        for i in range(3):
            obstacle = Obstacle(WIDTH + i * 300)
            self.obstacles.add(obstacle)

        # META FINAL (al final del mapa visible)
        self.goal = Goal(WIDTH - 50)

        self.font = pygame.font.Font(None, 80)
        self.completed = False
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_jumping and not self.game_over:
                self.is_jumping = True
                self.jump_velocity = -15
            if event.key == pygame.K_z and not self.game_over:
                self.shoot()

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

        # Balas contra enemigos
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                bullet.kill()
                enemy.health -= 1
                if enemy.health <= 0:
                    enemy.kill()

        # Jugador contra enemigos
        if pygame.sprite.spritecollideany(self.player_rect_to_sprite(), self.enemies):
            self.game_over = True

        # Jugador contra obstáculos
        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle.rect):
                self.player_rect.x -= 10

        # Verificar victoria (colisión con meta y sin enemigos)
        if self.player_rect.colliderect(self.goal.rect) and len(self.enemies) == 0:
            self.completed = True

        # Fondo animado
        self.bg_frame_counter += 1
        if self.bg_frame_counter >= self.bg_frame_rate:
            self.current_bg_frame = (self.current_bg_frame + 1) % len(self.background_frames)
            self.bg_frame_counter = 0

        return None

    def player_rect_to_sprite(self):
        temp = pygame.sprite.Sprite()
        temp.rect = self.player_rect
        return temp

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_frames[self.current_bg_frame], (0, 0))
        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image, obstacle.rect)
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        self.bullets.draw(self.screen)
        self.screen.blit(self.goal.image, self.goal.rect)
        frame = self.player_sprite.frames[self.player_sprite.current_frame]
        self.screen.blit(frame, self.player_rect)

        if self.completed:
            msg = self.font.render("NIVEL COMPLETADO", True, (0, 255, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        elif self.game_over:
            msg = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
