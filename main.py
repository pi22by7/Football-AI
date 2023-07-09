import math
import os
import sys
import pygame

from QLearning import QLearningPlayer

# Initialize Pygame
pygame.init()

DEBUG = True


def log(s):
    f = open("stats.log", "a")
    if DEBUG:
        f.write(s + "\n")
        print(s)
        f.close()


# Set up the screen
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abstract Football Field")

wants_ai = True

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the clock
clock = pygame.time.Clock()


class Player:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def move(self, keys):
        speed = 5
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * speed
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * speed

        # Update the player's position within the window boundaries
        new_x = self.x + dx
        new_y = self.y + dy
        self.x = max(0, min(new_x, WIDTH - self.size))
        self.y = max(0, min(new_y, HEIGHT - self.size))

        # log the direction the player is moving
        if dx < 0:
            log("Moving left")
        elif dx > 0:
            log("Moving right")

        if dy < 0:
            log("Moving up")
        elif dy > 0:
            log("Moving down")

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))


class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = 0
        self.speed_y = 0
        self.moving = False

    def move(self):
        if self.moving:
            self.x += self.speed_x
            self.y += self.speed_y
            self.apply_friction()
            self.check_boundaries()

    def apply_friction(self):
        self.speed_x *= 0.98
        self.speed_y *= 0.98

    def check_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)
        if distance <= self.radius + player.size:
            angle = math.atan2(dy, dx)
            kick_strength = 5
            self.speed_x = kick_strength * math.cos(angle)
            self.speed_y = kick_strength * math.sin(angle)
            overlap = self.radius + player.size - distance
            self.x += overlap * math.cos(angle)
            self.y += overlap * math.sin(angle)
            self.moving = True

    def check_boundaries(self):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.speed_x *= -1
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x *= -1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.speed_y *= -1
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.speed_y *= -1

    def reset_position(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.moving = False

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)


class Goalpost:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))


class Game:
    def __init__(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2, 50)
        self.ball = Ball(WIDTH // 4, HEIGHT // 4, 20)
        self.goalpost = Goalpost(WIDTH - 10, HEIGHT // 2 - 50, 10, 100)
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update_game(self, keys):
        self.player.move(keys)
        self.ball.check_collision(self.player)
        self.ball.move()
        self.check_goal()

    def check_goal(self):
        if (
                self.ball.x + self.ball.radius >= self.goalpost.x and self.ball.x - self.ball.radius <= self.goalpost.x
                + self.goalpost.width and
                self.ball.y + self.ball.radius >= self.goalpost.y and
                self.ball.y - self.ball.radius <= self.goalpost.y + self.goalpost.height
        ):
            self.score += 1
            self.ball.reset_position(WIDTH // 4, HEIGHT // 4)
            return True

    def reset_game(self):
        self.player.x = WIDTH // 2
        self.player.y = HEIGHT // 2
        self.ball.reset_position(WIDTH // 4, HEIGHT // 4)
        self.score = 0

    def draw_game(self):
        screen.fill(WHITE)
        self.player.draw()
        self.ball.draw()
        self.goalpost.draw()
        self.draw_score()
        pygame.display.update()
        pygame.display.flip()  # Add this line to update the display

    def draw_score(self):
        font = pygame.font.SysFont("Segoe UI", 36)
        score_text = font.render(f"Score: {self.score}", True, BLUE)
        screen.blit(score_text, (20, 20))

    def train(self):
        player = QLearningPlayer(actions=['up', 'down', 'left', 'right'])

        q_table_file = 'q_values.pkl'
        if os.path.exists(q_table_file):
            # Load the pre-trained Q-table
            # player.load_q_values(q_table_file)
            log("Loaded Q-values")
        else:
            # Training loop
            num_episodes = 1
            for episode in range(num_episodes):
                self.reset_game()

                while True:
                    state = [self.player.x, self.player.y, self.ball.x, self.ball.y, self.ball.speed_x,
                             self.ball.speed_y]

                    action = player.get_action(state)

                    keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}
                    if action == 'up':
                        keys[pygame.K_UP] = True
                    elif action == 'down':
                        keys[pygame.K_DOWN] = True
                    elif action == 'left':
                        keys[pygame.K_LEFT] = True
                    elif action == 'right':
                        keys[pygame.K_RIGHT] = True

                    self.update_game(keys)

                    next_state = [self.player.x, self.player.y, self.ball.x, self.ball.y, self.ball.speed_x,
                                  self.ball.speed_y]
                    reward = 0

                    if self.score >= 1:
                        break

                    if self.check_goal():
                        reward = 1

                    player.update_q_value(state, action, next_state, reward)

            player.save_q_values(q_table_file)
            log("Saved Q-values")

    def run(self):
        if wants_ai:
            self.train()

        while True:
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.update_game(keys)
            self.draw_game()
            clock.tick(60)


# Init the game
game = Game()

# Run the game
game.run()

log(game.score)
