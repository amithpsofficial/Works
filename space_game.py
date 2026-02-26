import pygame
import random
import math
import os

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elite Space Shooter")

clock = pygame.time.Clock()

# Colors
WHITE = (255,255,255)
RED = (255,60,60)
ORANGE = (255,180,0)
BLUE = (80,160,255)
GREEN = (60,255,120)
BLACK = (10,10,25)
YELLOW = (255,255,100)

font = pygame.font.SysFont("Arial", 26)
big_font = pygame.font.SysFont("Arial", 60)

# ---------------- HIGH SCORE ----------------
high_score = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())

# ---------------- GAME STATE ----------------
MENU = 0
PLAYING = 1
GAME_OVER = 2
state = MENU

# ---------------- BUTTON CLASS ----------------
class Button:
    def __init__(self, text, x, y, width, height, base_color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=12)

        text_surf = font.render(self.text, True, WHITE)
        surface.blit(
            text_surf,
            (self.rect.centerx - text_surf.get_width()//2,
             self.rect.centery - text_surf.get_height()//2)
        )

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# ---------------- RESET GAME ----------------
def reset_game():
    global player, bullets, enemies, powerups
    global score, level, player_health
    
    player = pygame.Rect(WIDTH//2-35, HEIGHT-80, 70, 25)
    bullets = []
    enemies = []
    powerups = []
    score = 0
    level = 1
    player_health = 100

reset_game()

# ---------------- MENU BUTTONS ----------------
start_button = Button("START GAME", WIDTH//2-120, HEIGHT//2, 240, 60, GREEN, BLUE)
quit_button = Button("QUIT", WIDTH//2-120, HEIGHT//2+90, 240, 60, RED, ORANGE)

# ---------------- GAME OVER BUTTONS ----------------
play_again_button = Button("PLAY AGAIN", WIDTH//2-120, HEIGHT//2, 240, 60, GREEN, BLUE)
menu_button = Button("MAIN MENU", WIDTH//2-120, HEIGHT//2+90, 240, 60, ORANGE, RED)

# ---------------- STARS ----------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(120)]
def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 2)
        star[1] += 2
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0

# ---------------- HEALTH BAR ----------------
def draw_health_bar(x, y, health, max_health):
    ratio = health / max_health
    pygame.draw.rect(screen, RED, (x, y, 200, 20))
    pygame.draw.rect(screen, GREEN, (x, y, 200 * ratio, 20))

# ---------------- PLAYER SHIP ----------------
def draw_player_ship(player_rect):
    x, y = player_rect.x, player_rect.y
    w, h = player_rect.width, player_rect.height

    body_points = [
        (x + w//2, y),
        (x, y + h),
        (x + w, y + h)
    ]
    pygame.draw.polygon(screen, GREEN, body_points)

    cockpit_center = (x + w//2, y + h//3)
    pygame.draw.circle(screen, BLUE, cockpit_center, w//6)

    left_wing = [(x, y + h//2), (x - w//4, y + 3*h//4), (x, y + 3*h//4)]
    right_wing = [(x + w, y + h//2), (x + w + w//4, y + 3*h//4), (x + w, y + 3*h//4)]
    pygame.draw.polygon(screen, RED, left_wing)
    pygame.draw.polygon(screen, RED, right_wing)

# ---------------- ENEMY ----------------
def draw_enemy(enemy_rect, angle=0):
    cx, cy = enemy_rect.center
    w, h = enemy_rect.width, enemy_rect.height
    points = [
        (cx, cy - h//2),
        (cx - w//2, cy),
        (cx, cy + h//2),
        (cx + w//2, cy)
    ]
    rotated_points = []
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    for px, py in points:
        dx = px - cx
        dy = py - cy
        rx = dx * cos_a - dy * sin_a + cx
        ry = dx * sin_a + dy * cos_a + cy
        rotated_points.append((rx, ry))
    pygame.draw.polygon(screen, RED, rotated_points)
    pygame.draw.polygon(screen, ORANGE, rotated_points, 2)

# ---------------- MAIN LOOP ----------------
running = True
spawn_timer = 0
shoot_cooldown = 0

while running:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if start_button.is_clicked(event):
                reset_game()
                state = PLAYING
            if quit_button.is_clicked(event):
                running = False

        elif state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and shoot_cooldown <= 0:
                    bullets.append(pygame.Rect(player.centerx-3, player.y, 6, 15))
                    shoot_cooldown = 15

        elif state == GAME_OVER:
            if play_again_button.is_clicked(event):
                reset_game()
                state = PLAYING
            if menu_button.is_clicked(event):
                state = MENU

    # ---------------- MENU ----------------
    if state == MENU:
        draw_stars()

        glow = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 255
        title_color = (int(glow), int(glow), 255)

        title = big_font.render("ELITE SPACE SHOOTER", True, title_color)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 150))



        start_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.update()
        continue

    # ---------------- PLAYING ----------------
    if state == PLAYING:

        draw_stars()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 7
        if keys[pygame.K_RIGHT] and player.x < WIDTH-player.width:
            player.x += 7

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        spawn_timer += 1
        if spawn_timer > max(15, 40 - level*2):
            enemies.append(pygame.Rect(random.randint(0, WIDTH-40), -40, 40, 40))
            spawn_timer = 0

        for bullet in bullets[:]:
            bullet.y -= 10
            if bullet.y < 0:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.y += 3 + level
            draw_enemy(enemy, pygame.time.get_ticks() % 360)

            if enemy.colliderect(player):
                player_health -= 10
                enemies.remove(enemy)

            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 1
                    break

        draw_player_ship(player)

        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, bullet)

        draw_health_bar(20, HEIGHT-40, player_health, 100)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (20,20))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (20,50))
        screen.blit(font.render(f"High Score: {high_score}", True, WHITE), (20,80))

        if player_health <= 0:
            if score > high_score:
                high_score = score
                with open("highscore.txt", "w") as f:
                    f.write(str(high_score))
            state = GAME_OVER

    # ---------------- GAME OVER ----------------
    if state == GAME_OVER:
        draw_stars()

        glow = abs(math.sin(pygame.time.get_ticks() * 0.004)) * 255
        over_color = (255, int(glow), int(glow))

        over = big_font.render("GAME OVER", True, over_color)
        screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 150))

        score_text = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 90))

        play_again_button.draw(screen)
        menu_button.draw(screen)

        pygame.display.update()
        continue

    pygame.display.update()

pygame.quit()