import pygame
import os
import random
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
        base_path = "assets/images/enemies/enemie_3/Walk.png"
        self.frames = self.load_frames(base_path, 64, 64, scale=2.0)
        self.index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = 1.5
        self.max_health = 3
        self.health = self.max_health

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

    def update(self):
        self.index += 0.2
        if self.index >= len(self.frames):
            self.index = 0
        self.image = self.frames[int(self.index)]
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        bar_width = self.rect.width
        bar_height = 6
        bg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fg_rect = pygame.Rect(self.rect.x, self.rect.y - 10, int(bar_width * (self.health / self.max_health)), bar_height)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(screen, (200, 0, 0), fg_rect)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        image_path = "assets/images/icons/obstacles/Pad_01_2.png"
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

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((12, 12))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -5

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = self.load_frames("assets/images/enemies/boss/Idle.png", 128, 128, scale=2)
        self.current_frame = 0
        self.animation_speed = 0.2
        self.image = self.frames[int(self.current_frame)]
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.health = 15
        self.attack_timer = 0
        self.attack_delay = 90
        self.dead = False

    def load_frames(self, path, fw, fh, scale=1):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sw, sh = sheet.get_size()
        for y in range(0, sh, fh):
            for x in range(0, sw, fw):
                frame = sheet.subsurface((x, y, fw, fh))
                frame = pygame.transform.smoothscale(frame, (int(fw * scale), int(fh * scale)))
                frames.append(frame)
        return frames

    def update(self):
        self.attack_timer += 1
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]

    def shoot(self, bullets_group):
        if self.dead:
            return
        if self.attack_timer >= self.attack_delay:
            offset_y = 80
            bullet = BossBullet(self.rect.centerx, self.rect.centery + offset_y)
            bullets_group.add(bullet)
            self.attack_timer = 0

class LevelThreeScreen:
    def __init__(self, screen, player_sprite):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.background_image = pygame.image.load("assets/images/level3/Cartoon_Forest_BG_02.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

        self.player_sprite = player_sprite
        self.player_frames = [pygame.transform.scale(f, (150, 150)).convert_alpha() for f in player_sprite.frames]
        self.player_rect = self.player_frames[0].get_rect(midbottom=(100, GROUND_Y))
        self.player_speed = 5
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 1

        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()

        for i in range(3):
            enemy = Enemy(WIDTH + i * 300, GROUND_Y)
            self.enemies.add(enemy)
        for i in range(2):
            obstacle = Obstacle(WIDTH + i * 400)
            self.obstacles.add(obstacle)

        self.boss = Boss(WIDTH - 150, GROUND_Y)

        font_path = "assets/fonts/PressStart2P-Regular.ttf"
        self.font = pygame.font.Font(font_path, 60)
        self.small_font = pygame.font.Font(font_path, 30)

        self.completed = False
        self.final_message = False
        self.completed_timer = 0   # <<< NUEVO
        self.game_over = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RETRY"
                elif event.key == pygame.K_m:
                    return "MENU"
        elif self.final_message:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
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
        if self.game_over:
            return None

        # --- Manejo del temporizador para mostrar el mensaje final después de "Nivel Completado"
        if self.completed:
            self.completed_timer += 1
            if self.completed_timer >= 180:  # 3 segundos (60FPS)
                self.final_message = True
                self.completed = False
            return None

        if self.final_message:
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
        self.boss.shoot(self.boss_bullets)

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

        if pygame.sprite.spritecollideany(self.player_rect_to_sprite(), self.enemies):
            self.game_over = True
        for bullet in self.boss_bullets:
            if self.player_rect.colliderect(bullet.rect):
                self.game_over = True

        for obstacle in self.obstacles:
            if self.player_rect.colliderect(obstacle.rect):
                self.player_rect.x -= 10

        # --- Activar mensaje de nivel completado antes del mensaje final
        if self.boss.dead and len(self.enemies) == 0 and self.player_rect.right >= WIDTH:
            self.completed = True
            self.completed_timer = 0

        return None

    def player_rect_to_sprite(self):
        temp = pygame.sprite.Sprite()
        temp.rect = self.player_rect
        return temp

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background_image, (0, 0))
        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image, obstacle.rect)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.bullets.draw(self.screen)
        self.boss_bullets.draw(self.screen)
        if not self.boss.dead:
            self.screen.blit(self.boss.image, self.boss.rect)

        frame = self.player_frames[self.player_sprite.current_frame]
        self.screen.blit(frame, self.player_rect)

        if self.final_message:
            msg = self.font.render("¡HAS COMPLETADO EL JUEGO!", True, (0, 255, 0))
            sub_msg = self.small_font.render("Presiona 'M' para volver al menú", True, (255, 255, 255))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 40))
            self.screen.blit(sub_msg, (WIDTH // 2 - sub_msg.get_width() // 2, HEIGHT // 2 + 40))
        elif self.completed:
            msg = self.font.render("NIVEL COMPLETADO", True, (0, 255, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        elif self.game_over:
            msg = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
            retry_msg = self.small_font.render("Presiona 'R' para Reintentar", True, (255, 255, 255))
            menu_msg = self.small_font.render("Presiona 'M' para volver al menú", True, (255, 255, 255))
            self.screen.blit(retry_msg, (WIDTH // 2 - retry_msg.get_width() // 2, HEIGHT // 2 + 80))
            self.screen.blit(menu_msg, (WIDTH // 2 - menu_msg.get_width() // 2, HEIGHT // 2 + 120))
