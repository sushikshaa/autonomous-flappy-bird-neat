import pygame
import random
import os
import neat

pygame.init()

# Window Setup
WIDTH, HEIGHT = 500, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Flappy Bird - Swarm AI")

# Assets
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.png")), (WIDTH, HEIGHT))
BIRD_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bird.png")), (45, 45))
PIPE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pipe.png")), (80, 500))

FONT = pygame.font.SysFont(None, 36)
GEN = 0

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.gravity = 0.5
        self.jump_strength = -8.5

    def jump(self):
        self.vel = self.jump_strength

    def move(self):
        self.vel += self.gravity
        self.y += self.vel

    def draw(self, win):
        win.blit(BIRD_IMG, (self.x, self.y))


class Pipe:
    GAP = 230  # Generous gap so multiple birds survive together
    VEL = 3.5

    def __init__(self, x):
        self.x = x
        self.height = random.randint(150, 390)
        self.top = self.height - 500
        self.bottom = self.height + self.GAP
        self.width = 80
        self.passed = False

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(PIPE_IMG, (self.x, self.top))
        win.blit(PIPE_IMG, (self.x, self.bottom))

    def collide(self, bird):
        bird_box = pygame.Rect(bird.x, bird.y, 40, 40)
        top_box = pygame.Rect(self.x, self.top, self.width, 500)
        bottom_box = pygame.Rect(self.x, self.bottom, self.width, 500)
        return bird_box.colliderect(top_box) or bird_box.colliderect(bottom_box)


def draw_window(win, birds, pipes, score, gen, alive):
    win.blit(BG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    for bird in birds:
        bird.draw(win)

    score_label = FONT.render(f"Score: {score}", True, (255, 255, 255))
    gen_label = FONT.render(f"Gen: {gen}", True, (255, 255, 255))
    alive_label = FONT.render(f"Alive Birds: {alive}", True, (255, 255, 255))

    win.blit(score_label, (10, 10))
    win.blit(gen_label, (10, 45))
    win.blit(alive_label, (10, 80))

    pygame.display.update()


def eval_genomes(genomes, config):
    global GEN
    GEN += 1

    nets = []
    ge = []
    birds = []

    # Spawn 30 birds with visible spacing
    for i, (_, genome) in enumerate(genomes):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(80, 260 + (i % 6) * 22))
        genome.fitness = 0
        ge.append(genome)

    pipes = [Pipe(WIDTH + 150)]
    clock = pygame.time.Clock()
    score = 0
    running = True

    while running and len(birds) > 0:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].width:
            pipe_ind = 1

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((
                bird.y,
                abs(bird.y - pipes[pipe_ind].height),
                abs(bird.y - pipes[pipe_ind].bottom)
            ))

            if output[0] > 0.5:
                bird.jump()

        # Handle pipes and collisions
        dead_birds = set()
        add_pipe = False
        rem = []

        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    dead_birds.add(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.width < 0:
                rem.append(pipe)

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(WIDTH + 100))

        for r in rem:
            pipes.remove(r)

        # Floor and ceiling collision
        for x, bird in enumerate(birds):
            if bird.y + 40 >= HEIGHT or bird.y < 0:
                dead_birds.add(x)

        # Remove dead birds safely
        for x in sorted(dead_birds, reverse=True):
            birds.pop(x)
            nets.pop(x)
            ge.pop(x)

        # STOP AT SCORE 20: Immediately end this generation and start the next
        if score >= 20:
            break

        draw_window(WIN, birds, pipes, score, GEN, len(birds))


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    p.run(eval_genomes, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)