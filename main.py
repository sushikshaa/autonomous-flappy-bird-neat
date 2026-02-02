import pygame
import random
import os

pygame.init()

# Screen
WIDTH, HEIGHT = 500, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load assets
BG = pygame.image.load(os.path.join("assets", "bg.png"))
BIRD = pygame.image.load(os.path.join("assets", "bird.png"))
PIPE = pygame.image.load(os.path.join("assets", "pipe.png"))
GAMEOVER = pygame.image.load(os.path.join("assets", "gameover.png"))

# Scale images
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))
BIRD = pygame.transform.scale(BIRD, (50, 50))
PIPE = pygame.transform.scale(PIPE, (80, 500))
GAMEOVER = pygame.transform.scale(GAMEOVER, (300, 150))

# Bird
bird_x = 100
bird_y = 350
bird_vel = 0
gravity = 0.5
jump = -10

# Pipes
pipe_width = 80
pipe_gap = 200
pipe_vel = 3
pipes = []

def create_pipe():
    height = random.randint(150, 450)
    pipes.append([WIDTH, height - 500, 500])  # top pipe
    pipes.append([WIDTH, height + pipe_gap, 500])  # bottom pipe

create_pipe()

score = 0
high_score = 0

font = pygame.font.SysFont(None, 50)

clock = pygame.time.Clock()

def draw_window():
    WIN.blit(BG, (0, 0))

    # draw bird
    WIN.blit(BIRD, (bird_x, bird_y))

    # draw pipes
    for i in range(0, len(pipes), 2):
        WIN.blit(PIPE, (pipes[i][0], pipes[i][1]))
        WIN.blit(PIPE, (pipes[i+1][0], pipes[i+1][1]))

    # Score
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    WIN.blit(score_text, (10, 10))

    high_score_text = font.render("High Score: " + str(high_score), True, (255, 255, 255))
    WIN.blit(high_score_text, (10, 50))

    pygame.display.update()

def game_over():
    WIN.blit(GAMEOVER, (100, 250))
    pygame.display.update()
    pygame.time.delay(2000)

# Main loop
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_vel = jump

    # Bird movement
    bird_vel += gravity
    bird_y += bird_vel

    # Pipes movement
    for i in range(0, len(pipes), 2):
        pipes[i][0] -= pipe_vel
        pipes[i+1][0] -= pipe_vel

        # Score
        if pipes[i][0] + pipe_width < bird_x and not pipes[i][0] + pipe_width < bird_x - pipe_vel:
            score += 1

    # Remove pipes
    if pipes[0][0] < -pipe_width:
        pipes.pop(0)
        pipes.pop(0)
        create_pipe()

    # Collision
    for i in range(0, len(pipes), 2):
        if bird_x + 25 > pipes[i][0] and bird_x - 25 < pipes[i][0] + pipe_width:
            if bird_y < pipes[i][1] + 500 or bird_y + 50 > pipes[i+1][1]:
                if score > high_score:
                    high_score = score
                game_over()
                running = False

    if bird_y > HEIGHT or bird_y < -50:
        if score > high_score:
            high_score = score
        game_over()
        running = False

    draw_window()

pygame.quit()
 