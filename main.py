import pygame
import asyncio
import random
import math
from enum import Enum


class State(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

pygame.init()


# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BALL_RADIUS = 10
NUM_BALLS = 40
BALL_SPEED = 1 
COUNT = 0
CHANCE_OF_CHASE = 0.6
NUM_PLAYERS_EACH_TEAM = 20
# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK=(0,0,0)

# Images
ROCK_IMAGE = pygame.transform.scale(pygame.image.load("graphics/rock.svg"), (BALL_RADIUS*2, BALL_RADIUS*2))
PAPER_IMAGE = pygame.transform.scale(pygame.image.load("graphics/paper.png"), (BALL_RADIUS*2, BALL_RADIUS*2))
SCISSORS_IMAGE = pygame.transform.scale(pygame.image.load("graphics/scissors.svg"), (BALL_RADIUS*2, BALL_RADIUS*2))

# Font
font = pygame.font.Font(None, 36)


# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Living RPS Clone")
game_active = True
players = []

def reset_game():
    global players
    global game_active
    players = []
    game_active = True
    for _ in range(NUM_PLAYERS_EACH_TEAM):
        for state in State:
            x = random.randint(BALL_RADIUS, WIDTH - BALL_RADIUS)
            y = random.randint(BALL_RADIUS, HEIGHT - BALL_RADIUS)
            angle = random.uniform(0, 2 * math.pi)  # Random initial direction
            if state == State.ROCK:
                image = ROCK_IMAGE
            elif state == State.PAPER:
                image = PAPER_IMAGE
            else:
                image = SCISSORS_IMAGE
            players.append({'state': state, 'x': x, 'y': y, 'angle': angle, 'image': image})

reset_game()

clock = pygame.time.Clock()

async def main():
    global game_active
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
        screen.fill(WHITE)
        for player in players:
            x, y, angle, state, image = player['x'], player['y'], player['angle'], player['state'], player['image']

            target_angle = None
            min_distance = float('inf')

            for other_player in players:
                if player != other_player and state != other_player['state']:
                    if (state == State.ROCK and other_player['state'] == State.SCISSORS) or \
                            (state == State.PAPER and other_player['state'] == State.ROCK) or \
                            (state == State.SCISSORS and other_player['state'] == State.PAPER):
                        if random.random() <= CHANCE_OF_CHASE: # Chance of it deciding to not chase this player
                            continue
                        distance = math.sqrt((x - other_player['x']) ** 2 + (y - other_player['y']) ** 2)
                        if distance < min_distance:
                            min_distance = distance
                            target_angle = math.atan2(other_player['y'] - y, other_player['x'] - x)

            if target_angle is not None:
                angle_diff = target_angle - angle
                if angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                if angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                angle += 0.05 * angle_diff

            # Update the ball's position
            bonus_speed = 0.3 if random.random() < 0.1 else 0 
                
            x += (BALL_SPEED + bonus_speed) * math.cos(angle)
            y += (BALL_SPEED + bonus_speed) * math.sin(angle)

            # Bounce off the walls
            if x - BALL_RADIUS <= 0 or x + BALL_RADIUS >= WIDTH:
                angle = math.pi - angle
            if y - BALL_RADIUS <= 0 or y + BALL_RADIUS >= HEIGHT:
                angle = -angle

            # Check for collisions with other balls
            for other_player in players:
                if player != other_player:
                    distance = math.sqrt((x - other_player['x']) ** 2 + (y - other_player['y']) ** 2)
                    if distance < 2 * BALL_RADIUS:
                        # Handle collisions based on colors
                        if state == State.ROCK and other_player['state'] == State.SCISSORS:
                            other_player['state'] = State.ROCK
                            other_player['image'] = ROCK_IMAGE
                        elif state == State.PAPER and other_player['state'] == State.ROCK:
                            other_player['state'] = State.PAPER
                            other_player['image'] = PAPER_IMAGE
                        elif state == State.SCISSORS and other_player['state'] == State.PAPER:
                            other_player['state'] = State.SCISSORS
                            other_player['image'] = SCISSORS_IMAGE
            player['x'] = x
            player['y'] = y
            player['angle'] = angle

            # Draw the ball
            screen.blit(image, (int(x - BALL_RADIUS), int(y - BALL_RADIUS)))

            text = font.render("Press SPACE to reset", True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            if not game_active:
                screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)
        if all(player['state'] == players[0]['state'] for player in players):
            game_active = False

            pygame.display.flip()
        await asyncio.sleep(0)
asyncio.run(main())