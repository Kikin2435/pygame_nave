import pygame
import random

# Inicializar Pygame
pygame.init()

# Crear una ventana de despliegue
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
WHITE = (255, 255, 255)
RED = (255, 0, 0)
screen.fill(WHITE)
pygame.display.set_caption("Detección de colisiones")

# Ajuste del reloj y los cuadros por segundo (FPS)
FPS = 60
clock = pygame.time.Clock()

# Ajustar variables
VELOCITY = 5
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

# Carga de imágenes
dragon_image = pygame.image.load("nave.png")
enemy_image = pygame.image.load("bicho.png")
heart_image = pygame.image.load("corazon.png")  # Cargar la imagen del corazón

# Ajustar tamaño del corazón
heart_image = pygame.transform.scale(heart_image, (30, 30))

# Proyectiles
projectiles = []
projectile_image = pygame.Surface((5, 10))
projectile_image.fill((255, 0, 0))

# Enemigos
enemies = []

# Power-ups
powerups = []
powerup_effect_time = 10000  # 10 segundos de efecto para los power-ups

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
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    restart_text = font.render("Presiona Enter para reiniciar", True, (0, 0, 0))
    
    screen.fill(WHITE)
    screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//3))
    screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2))
    
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

def spawn_powerup():
    powerup_type = random.choice(["triple_shot", "extra_life", "freeze_enemies"])
    powerup_rect = None

    if powerup_type == "triple_shot":
        powerup_rect = pygame.Rect(random.randint(0, WINDOW_WIDTH-20), 0, 20, 20)
        powerups.append(("triple_shot", powerup_rect, (255, 0, 0)))

    elif powerup_type == "extra_life" and lives < max_lives:
        powerup_rect = pygame.Rect(random.randint(0, WINDOW_WIDTH-30), 0, 30, 30)
        powerups.append(("extra_life", powerup_rect, heart_image))

    elif powerup_type == "freeze_enemies":
        powerup_rect = pygame.Rect(random.randint(0, WINDOW_WIDTH-20), 0, 20, 20)
        powerups.append(("freeze_enemies", powerup_rect, (0, 0, 255)))

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

        if event.type == SPAWN_ENEMY_EVENT and not freeze_enemies_active:
            for _ in range(1 + score // 10):
                enemy_rect = enemy_image.get_rect(center=(random.randint(0, WINDOW_WIDTH - enemy_image.get_width()), 0))
                enemies.append(enemy_rect)

        if event.type == SPAWN_POWERUP_EVENT:
            spawn_powerup()

        if event.type == TRIPLE_SHOT_EVENT:
            triple_shot_active = False
            PROJECTILE_VELOCITY = 7  # Restablecer la velocidad de disparo

        if event.type == FREEZE_ENEMIES_EVENT:
            freeze_enemies_active = False

    # Leer la lista de las teclas que están presionadas
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dragon_rect.x -= VELOCITY
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dragon_rect.x += VELOCITY
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dragon_rect.y -= VELOCITY
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dragon_rect.y += VELOCITY

    # Mantener el dragón dentro de los límites de la pantalla
    dragon_rect.x = max(0, min(dragon_rect.x, WINDOW_WIDTH - dragon_rect.width))
    dragon_rect.y = max(0, min(dragon_rect.y, WINDOW_HEIGHT - dragon_rect.height))

    # Mover los proyectiles
    for projectile in projectiles[:]:
        projectile.y -= PROJECTILE_VELOCITY
        if projectile.bottom < 0:
            projectiles.remove(projectile)

    # Mover los enemigos
    for enemy in enemies[:]:
        if not freeze_enemies_active:
            enemy.y += ENEMY_VELOCITY
        if enemy.top > WINDOW_HEIGHT:
            enemies.remove(enemy)
        elif dragon_rect.colliderect(enemy):
            enemies.remove(enemy)
            lives -= 1  # Reducir una vida si un enemigo toca la nave
            
            # Mostrar pantalla roja por 0.1 segundos
            screen.fill(RED)
            pygame.display.flip()
            pygame.time.delay(100)  # Espera 0.1 segundos
            screen.fill(WHITE)
            
            if lives <= 0:
                game_over()

    # Detección de colisiones entre proyectiles y enemigos
    for projectile in projectiles[:]:
        for enemy in enemies[:]:
            if projectile.colliderect(enemy):
                enemies.remove(enemy)
                projectiles.remove(projectile)
                score += 1
                if score % 10 == 0:
                    enemy_spawn_rate = max(200, enemy_spawn_rate - 100)
                    pygame.time.set_timer(SPAWN_ENEMY_EVENT, enemy_spawn_rate)
                break

    # Mover y gestionar power-ups
    for powerup in powerups[:]:
        powerup_rect = powerup[1]
        powerup_rect.y += 5  # Velocidad del power-up

        if dragon_rect.colliderect(powerup_rect):
            if powerup[0] == "triple_shot":
                triple_shot_active = True
                PROJECTILE_VELOCITY = 15  # Incrementar velocidad de disparo
                pygame.time.set_timer(TRIPLE_SHOT_EVENT, powerup_effect_time)  # Uso el mismo evento para regresar la velocidad
            elif powerup[0] == "extra_life" and lives < max_lives:
                lives += 1
            elif powerup[0] == "freeze_enemies":
                freeze_enemies_active = True
                pygame.time.set_timer(FREEZE_ENEMIES_EVENT, powerup_effect_time)
            powerups.remove(powerup)

        elif powerup_rect.top > WINDOW_HEIGHT:
            powerups.remove(powerup)

    # Dibujar todo en la pantalla
    screen.fill(WHITE)
    screen.blit(dragon_image, dragon_rect)

    for projectile in projectiles:
        screen.blit(projectile_image, projectile)

    for enemy in enemies:
        screen.blit(enemy_image, enemy)

    for powerup in powerups:
        pygame.draw.rect(screen, powerup[2], powerup[1])  # Dibuja el power-up en el color correspondiente

    # Mostrar la puntuación
    score_text = font.render(f"Puntaje: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Mostrar las vidas usando corazones
    for i in range(lives):
        screen.blit(heart_image, (WINDOW_WIDTH - (i + 1) * (heart_image.get_width() + 10) - 20, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
 







