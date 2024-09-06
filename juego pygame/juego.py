import pygame
import random
import json
import os

# Inicializar Pygame
pygame.init()

# Crear una ventana de despliegue
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
screen.fill(WHITE)
pygame.display.set_caption("Detección de colisiones")

# Ajuste del reloj y los cuadros por segundo (FPS)
FPS = 60
clock = pygame.time.Clock()

# Ajustar variables
VELOCITY = 10
PROJECTILE_VELOCITY = 7
ENEMY_VELOCITY = 2
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
SPAWN_POWERUP_EVENT = pygame.USEREVENT + 2
TRIPLE_SHOT_EVENT = pygame.USEREVENT + 3
FREEZE_ENEMIES_EVENT = pygame.USEREVENT + 4

pygame.time.set_timer(SPAWN_ENEMY_EVENT, 1000)  # Crear un nuevo enemigo cada segundo
pygame.time.set_timer(SPAWN_POWERUP_EVENT, 10000)  # Crear un nuevo power-up cada 10 segundos
score = 0
lives = 3
max_lives = 5
enemy_spawn_rate = 1000  # Tiempo inicial de aparición de enemigos (en ms)
triple_shot_active = False
freeze_enemies_active = False

# Cargar fuentes
font = pygame.font.SysFont(None, 55)
small_font = pygame.font.SysFont(None, 36)

# Carga de imágenes
dragon_image = pygame.image.load("nave.png")
heart_image = pygame.image.load("corazon.png")  # Cargar la imagen del corazón
triple_shot_image = pygame.image.load("triple.png")  # Cargar la imagen del power-up de disparo triple
freeze_image = pygame.image.load("copo.png")  # Cargar la imagen del power-up de congelar enemigos

# Cargar el sonido de pérdida de vida
life_loss_sound = pygame.mixer.Sound("aldeano.wav")

# Ajustar tamaño del corazón
heart_image = pygame.transform.scale(heart_image, (30, 30))
triple_shot_image = pygame.transform.scale(triple_shot_image, (20, 20))
freeze_image = pygame.transform.scale(freeze_image, (20, 20))

# Cargar imágenes de enemigos, excluyendo la con terminación _12
enemy_images = [pygame.image.load(f"bicho_colored_{i}.png") for i in range(1, 16) if i != 12]

# Proyectiles
projectiles = []
projectile_image = pygame.Surface((5, 10))
projectile_image.fill((255, 0, 0))

# Enemigos
enemies = []

# Power-ups
powerups = []
powerup_effect_time = 10000  # 10 segundos de efecto para los power-ups

# Carga la imagen del fondo para la pantalla de inicio
background_image = pygame.image.load("iGu.gif")
background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

def show_start_screen():
    global player_name
    input_box = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 25, 300, 50)
    color_inactive = pygame.Color('WHITE')
    color_active = pygame.Color('WHITE')
    color = color_inactive
    font = pygame.font.Font(None, 48)
    text = ''
    active = True
    done = False

    while not done:
        screen.blit(background_image, (0, 0))  # Cambia screen.fill() por blit()

        # Mostrar el texto de entrada
        txt_surface = font.render(text, True, color)
        width = max(300, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        # Mostrar instrucciones
        instructions = font.render("Ingresa tu nombre y presiona Enter", True, WHITE)
        screen.blit(instructions, (WINDOW_WIDTH // 2 - instructions.get_width() // 2, WINDOW_HEIGHT // 2 - 75))

        # Mostrar el mensaje para comenzar
        restart_text = font.render("Presiona Enter para comenzar", True, WHITE)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 75))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and text:
                    player_name = text
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        pygame.display.flip()
        clock.tick(30)

def show_high_scores():
    if not os.path.isfile("high_scores.json"):
        with open("high_scores.json", "w") as f:
            json.dump([], f)

    with open("high_scores.json", "r") as f:
        high_scores = json.load(f)

    high_scores.append({"name": player_name, "score": score})
    high_scores = sorted(high_scores, key=lambda x: x['score'], reverse=True)[:5]

    with open("high_scores.json", "w") as f:
        json.dump(high_scores, f)

    screen.fill(DARK_BLUE)
    
    title_text = font.render("High Scores", True, WHITE)
    screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 50))

    y_offset = 100
    for idx, entry in enumerate(high_scores):
        score_text = font.render(f"{idx + 1}. {entry['name']} - {entry['score']}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, y_offset))
        y_offset += 50

    restart_text = small_font.render("Presiona Enter para reiniciar", True, WHITE)
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT - 100))

    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    reset_game()

def reset_game():
    global score, enemy_spawn_rate, enemies, projectiles, dragon_rect, lives, triple_shot_active, freeze_enemies_active
    score = 0
    lives = 3
    enemy_spawn_rate = 1000
    enemies = []
    projectiles = []
    powerups.clear()
    triple_shot_active = False
    freeze_enemies_active = False
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, enemy_spawn_rate)
    dragon_rect.topleft = (WINDOW_WIDTH // 2, 500)

def game_over():
    show_high_scores()

def spawn_powerup():
    powerup_type = random.choice(["triple_shot", "extra_life", "freeze_enemies"])
    powerup_rect = None

    if powerup_type == "triple_shot":
        powerup_rect = pygame.Rect(random.randint(0, WINDOW_WIDTH-20), 0, 20, 20)
        powerups.append(("triple_shot", powerup_rect, triple_shot_image))

    elif powerup_type == "extra_life" and lives < max_lives:
        powerup_rect = pygame.Rect(random.randint(0, WINDOW_WIDTH-30), 0, 30, 30)
        powerups.append(("extra_life", powerup_rect, heart_image))

    elif powerup_type == "freeze_enemies":
        powerup_rect = pygame.Rect(random.randint(0, WINDOW_WIDTH-20), 0, 20, 20)
        powerups.append(("freeze_enemies", powerup_rect, freeze_image))

# Pantalla de inicio para ingresar el nombre del jugador
player_name = ""
show_start_screen()

# Ciclo principal de pygame
running = True
dragon_rect = dragon_image.get_rect()
reset_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if triple_shot_active:
                projectiles.append(pygame.Rect(dragon_rect.centerx, dragon_rect.top, 5, 10))
                projectiles.append(pygame.Rect(dragon_rect.centerx - 10, dragon_rect.top, 5, 10))
                projectiles.append(pygame.Rect(dragon_rect.centerx + 10, dragon_rect.top, 5, 10))
            else:
                projectiles.append(pygame.Rect(dragon_rect.centerx, dragon_rect.top, 5, 10))

        if event.type == SPAWN_ENEMY_EVENT:
            if not freeze_enemies_active:
                enemy_image = random.choice(enemy_images)
                enemy_rect = enemy_image.get_rect()
                enemy_rect.x = random.randint(0, WINDOW_WIDTH - enemy_rect.width)
                enemy_rect.y = -enemy_rect.height
                enemies.append((enemy_rect, enemy_image))

        if event.type == SPAWN_POWERUP_EVENT:
            spawn_powerup()

        if event.type == TRIPLE_SHOT_EVENT:
            triple_shot_active = False
            PROJECTILE_VELOCITY = 7

        if event.type == FREEZE_ENEMIES_EVENT:
            freeze_enemies_active = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dragon_rect.x -= VELOCITY
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dragon_rect.x += VELOCITY
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dragon_rect.y -= VELOCITY
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dragon_rect.y += VELOCITY

    dragon_rect.x = max(0, min(dragon_rect.x, WINDOW_WIDTH - dragon_rect.width))
    dragon_rect.y = max(0, min(dragon_rect.y, WINDOW_HEIGHT - dragon_rect.height))

    # Mover los proyectiles
    for projectile in projectiles[:]:
        projectile.y -= PROJECTILE_VELOCITY
        if projectile.bottom < 0:
            projectiles.remove(projectile)
        else:
            # Detectar colisión con enemigos
            for enemy in enemies[:]:
                enemy_rect, enemy_image = enemy
                if projectile.colliderect(enemy_rect):
                    projectiles.remove(projectile)
                    enemies.remove(enemy)
                    score += 1  # Incrementar el puntaje en 10 por cada enemigo eliminado
                    break

    # Mover los enemigos
    for enemy in enemies[:]:
        enemy_rect, enemy_image = enemy
        if not freeze_enemies_active:
            enemy_rect.y += ENEMY_VELOCITY
        if enemy_rect.top > WINDOW_HEIGHT:
            enemies.remove(enemy)
        elif dragon_rect.colliderect(enemy_rect):
            enemies.remove(enemy)
            lives -= 1
            life_loss_sound.play()  # Reproducir el sonido de pérdida de vidad
            screen.fill(RED)
            pygame.display.flip()
            pygame.time.wait(100)
            if lives <= 0:
                game_over()

    # Mover los power-ups
    for powerup in powerups[:]:
        powerup_type, powerup_rect, powerup_image = powerup
        powerup_rect.y += ENEMY_VELOCITY
        if powerup_rect.top > WINDOW_HEIGHT:
            powerups.remove(powerup)
        elif dragon_rect.colliderect(powerup_rect):
            if powerup_type == "triple_shot":
                triple_shot_active = True
                pygame.time.set_timer(TRIPLE_SHOT_EVENT, powerup_effect_time)
            elif powerup_type == "extra_life":
                if lives < max_lives:
                    lives += 1
            elif powerup_type == "freeze_enemies":
                freeze_enemies_active = True
                pygame.time.set_timer(FREEZE_ENEMIES_EVENT, powerup_effect_time)
            powerups.remove(powerup)

    screen.fill(BLACK)
    
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    
    lives_text = font.render("Vidas:", True, BLACK)
    screen.blit(lives_text, (WINDOW_WIDTH - 150, 10))
    
    # Ajustar el ancho de la imagen del corazón y el espacio entre ellos
    heart_width = heart_image.get_width()
    padding = 10  # Espacio entre los corazones

    for i in range(lives):
        x_position = WINDOW_WIDTH - (heart_width + padding) * (max_lives - i) - padding
        screen.blit(heart_image, (x_position, 40))

    screen.blit(dragon_image, dragon_rect)

    for enemy_rect, enemy_image in enemies:
        screen.blit(enemy_image, enemy_rect)

    for projectile in projectiles:
        screen.blit(projectile_image, projectile)

    for powerup_type, powerup_rect, powerup_image in powerups:
        screen.blit(powerup_image, powerup_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()