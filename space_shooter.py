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

# ---------------- RESET GAME ----------------
def reset_game():
    global player, bullets, enemies, powerups
    global score, level, player_health
    global boss, boss_health, boss_active
    global boss_bullets, rapid_fire, rapid_timer
    global boss_attack_timer, boss_pattern
    
    player = pygame.Rect(WIDTH//2-35, HEIGHT-80, 70, 25)
    bullets = []
    enemies = []
    powerups = []
    score = 0
    level = 1
    player_health = 100
    
    boss = None
    boss_health = 200
    boss_active = False
    boss_bullets = []
    
    boss_attack_timer = 0
    boss_pattern = 0
    
    rapid_fire = False
    rapid_timer = 0

reset_game()

# ---------------- STARS ----------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(120)]
def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 2)
        star[1] += 2 + level
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

    # Main body (arrowhead)
    body_points = [
        (x + w//2, y),
        (x, y + h),
        (x + w, y + h)
    ]
    pygame.draw.polygon(screen, GREEN, body_points)

    # Cockpit
    cockpit_center = (x + w//2, y + h//3)
    pygame.draw.circle(screen, BLUE, cockpit_center, w//6)

    # Wings
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
    pygame.draw.polygon(screen, ORANGE, rotated_points, 2)  # outline

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                reset_game()
                state = PLAYING

        elif state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and shoot_cooldown <= 0:
                    bullets.append(pygame.Rect(player.centerx-3, player.y, 6, 15))
                    shoot_cooldown = 5 if rapid_fire else 15

        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
                state = PLAYING

    if state == MENU:
        title = big_font.render("ELITE SPACE SHOOTER", True, WHITE)
        start = font.render("Press ENTER to Start", True, GREEN)
        screen.blit(title, (WIDTH//2-260, HEIGHT//2-100))
        screen.blit(start, (WIDTH//2-160, HEIGHT//2))
        pygame.display.update()
        continue

    if state == PLAYING:

        draw_stars()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 7
        if keys[pygame.K_RIGHT] and player.x < WIDTH-player.width:
            player.x += 7

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if score >= level * 15 and not boss_active:
            level += 1

        # ---------------- BOSS ----------------
        if level % 5 == 0 and not boss_active and score > 0:
            boss = pygame.Rect(WIDTH//2-100, 60, 200, 100)
            boss_health = 200 + level * 50
            boss_active = True
            boss_pattern = random.randint(0,2)

        # ---------------- SPAWN ENEMIES ----------------
        if not boss_active:
            spawn_timer += 1
            if spawn_timer > max(15, 40 - level*2):
                enemies.append(pygame.Rect(random.randint(0, WIDTH-40), -40, 40, 40))
                spawn_timer = 0

        # ---------------- BULLETS ----------------
        for bullet in bullets[:]:
            bullet.y -= 10
            if bullet.y < 0:
                bullets.remove(bullet)

        # ---------------- ENEMIES ----------------
        for enemy in enemies[:]:
            enemy.y += 3 + level
            angle = pygame.time.get_ticks() % 360
            draw_enemy(enemy, angle)

            if enemy.colliderect(player):
                player_health -= 10
                enemies.remove(enemy)

            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 1
                    break

        # ---------------- POWERUPS ----------------
        for p in powerups[:]:
            p[1] += 3
            color = GREEN if p[2] == "health" else YELLOW
            pygame.draw.circle(screen, color, (p[0], p[1]), 10)

            if player.collidepoint(p[0], p[1]):
                if p[2] == "health":
                    player_health = min(100, player_health + 20)
                else:
                    rapid_fire = True
                    rapid_timer = 300
                powerups.remove(p)

        if rapid_fire:
            rapid_timer -= 1
            if rapid_timer <= 0:
                rapid_fire = False

        # ---------------- BOSS ----------------
        if boss_active:
            pygame.draw.rect(screen, BLUE, boss)

            boss_attack_timer += 1
            boss.x += 3
            if boss.right >= WIDTH or boss.left <= 0:
                boss.x -= 6

            if boss_attack_timer % 240 == 0:
                boss_pattern = random.randint(0,2)

            # Aimed shot
            if boss_pattern == 0 and boss_attack_timer % 40 == 0:
                dx = player.centerx - boss.centerx
                dy = player.centery - boss.centery
                dist = math.hypot(dx, dy)
                dx, dy = dx/dist, dy/dist
                boss_bullets.append([boss.centerx, boss.bottom, dx*6, dy*6])

            # Spread shot
            if boss_pattern == 1 and boss_attack_timer % 60 == 0:
                for angle in [-0.3, 0, 0.3]:
                    dx = math.sin(angle)
                    dy = 1
                    boss_bullets.append([boss.centerx, boss.bottom, dx*6, dy*6])

            # Radial burst
            if boss_pattern == 2 and boss_attack_timer % 120 == 0:
                for angle in range(0, 360, 20):
                    rad = math.radians(angle)
                    dx = math.cos(rad)
                    dy = math.sin(rad)
                    boss_bullets.append([boss.centerx, boss.centery, dx*4, dy*4])

            # Update boss bullets
            for b in boss_bullets[:]:
                b[0] += b[2]
                b[1] += b[3]
                pygame.draw.circle(screen, YELLOW, (int(b[0]), int(b[1])), 5)

                if player.collidepoint(b[0], b[1]):
                    player_health -= 10
                    boss_bullets.remove(b)
                elif b[1] > HEIGHT or b[0] < 0 or b[0] > WIDTH:
                    boss_bullets.remove(b)

            for bullet in bullets[:]:
                if boss.colliderect(bullet):
                    boss_health -= 5
                    bullets.remove(bullet)

            if boss_health <= 0:
                boss_active = False
                boss_bullets.clear()
                score += 40

            draw_health_bar(WIDTH//2-100, 20, boss_health, 200 + level*50)

        # ---------------- DRAW PLAYER ----------------
        draw_player_ship(player)

        # Draw bullets
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
        over = big_font.render("GAME OVER", True, RED)
        restart = font.render("Press R to Restart", True, GREEN)
        screen.blit(over, (WIDTH//2-170, HEIGHT//2-80))
        screen.blit(restart, (WIDTH//2-150, HEIGHT//2))
        pygame.display.update()
        continue

    pygame.display.update()

pygame.quit()
