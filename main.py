import pygame
import sys
import math

from QLearning import QLearningPlayer

DEBUG = True


def log(s):
    if DEBUG:
        print(s)


# Initialize Pygame
pygame.init()
log("init")

# Set up the screen
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Abstract Football Field")

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
        self.speed_x = 1
        self.speed_y = 1

    def move(self, keys):
        if (pygame.K_LEFT is True in keys) and self.x > 0:
            print("left")
            self.x -= 5
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.size:
            print("right")
            self.x += 5
        if keys[pygame.K_UP] and self.y > 0:
            print("up")
            self.y -= 5
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.size:
            print("down")
            self.y += 5
        # self.x = max(0, min(self.x + (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5, WIDTH - self.size))
        # self.y = max(0, min(self.y + (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 5, HEIGHT - self.size))

    # def move(self, keys):
    #     speed = 5
    #     move_x = 0
    #     move_y = 0
    #
    #     if pygame.K_LEFT in keys:
    #         move_x -= speed
    #     if pygame.K_RIGHT in keys:
    #         move_x += speed
    #     if pygame.K_UP in keys:
    #         move_y -= speed
    #     if pygame.K_DOWN in keys:
    #         move_y += speed

    #     self.x = max(0, min(self.x + move_x, WIDTH - self.size))
    #     self.y = max(0, min(self.y + move_y, HEIGHT - self.size))

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
        # log("collided")
        ball_rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        player_rect = pygame.Rect(
            player.x,
            player.y,
            player.size,
            player.size
        )

        if ball_rect.colliderect(player_rect):
            dx = self.x - player.x
            dy = self.y - player.y
            angle = math.atan2(dy, dx)
            kick_strength = 5
            self.speed_x = kick_strength * math.cos(angle)
            self.speed_y = kick_strength * math.sin(angle)

            overlap_x = (self.radius + player.size) * math.cos(angle)
            overlap_y = (self.radius + player.size) * math.sin(angle)
            self.x = player.x + (player.size // 2) + overlap_x
            self.y = player.y + (player.size // 2) + overlap_y

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

    def update_game(self):
        # event = pygame.event.get()
        # keys = pygame.key.get_pressed()
        # print(keys)
        # self.player.move(keys)

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

    def draw_score(self):
        font = pygame.font.SysFont("Segoe UI", 36)
        score_text = font.render(f"Score: {self.score}", True, BLUE)
        screen.blit(score_text, (20, 20))

    def run(self):
        while True:
            self.handle_events()
            self.update_game()
            self.draw_game()
            clock.tick(75)


# Init the game
game = Game()
player = QLearningPlayer(actions=['up', 'down', 'left', 'right'])
# Training loop
num_episodes = 1
for episode in range(num_episodes):
    # Reset the game state for each episode
    game.reset_game()

    while True:
        # Get the current game state
        state = [game.player.x, game.player.y, game.ball.x, game.ball.y, game.ball.speed_x, game.ball.speed_y]

        # Choose an action based on the current state
        action = player.get_action(state)

        # Perform the chosen action
        if action == 'up':
            keys = {pygame.K_UP: True, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}
        elif action == 'down':
            keys = {pygame.K_UP: False, pygame.K_DOWN: True, pygame.K_LEFT: False, pygame.K_RIGHT: False}
        elif action == 'left':
            keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: True, pygame.K_RIGHT: False}
        elif action == 'right':
            keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: True}
        else:
            keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_LEFT: False, pygame.K_RIGHT: False}

        game.player.move(keys)
        # Update the game state
        game.update_game()

        # Get the new game state and reward
        next_state = [game.player.x, game.player.y, game.ball.x, game.ball.y, game.ball.speed_x, game.ball.speed_y]
        reward = 0
        print(reward, game.score)
        if game.score >= 1:
            # The player has scored at least 3 goals, end the episode
            break

        if game.check_goal():
            # The ball has touched the goalpost, give a positive reward
            reward = 1

        # Update the Q-value for the current state-action pair
        player.update_q_value(state, action, next_state, reward)

# Run the game
game.run()
