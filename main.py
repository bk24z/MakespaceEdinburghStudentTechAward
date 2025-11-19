from unittest.mock import DEFAULT

import pygame
import time
import math
from enum import Enum, auto

pygame.init()

FRAMES_PER_SECOND = 60

# Measurements
# All lane, ball, pin measurements are in inches (to align with industry standards)
LANE_WIDTH = 41.5
GUTTER_WIDTH = 9.25
ALLEY_WIDTH = LANE_WIDTH + GUTTER_WIDTH * 2
LANE_LENGTH = 65 * 12  # 90 feet TODO: Needs to be checked
APPROACH_LENGTH = 15 * 12  # 15 feet
LEFT_BOUNDARY = -(LANE_WIDTH / 2)
RIGHT_BOUNDARY = (LANE_WIDTH / 2)

# TODO: Change these to be more accurate later
FOUL_LINE_TO_FRONT_PIN_DISTANCE = 60 * 12  # 60 feet
FOUL_LINE_TO_END_DISTANCE = None
PIN_SPACING_H = 12
HALF_PIN_SPACING_H = PIN_SPACING_H / 2
PIN_SPACING_V = 20.75 / 2
# FOUL_LINE_TO_FRONT_PIN_DISTANCE = 55 * 12  # 60 feet
# PIN_SPACING_H = 12
# HALF_PIN_SPACING_H = PIN_SPACING_H
# PIN_SPACING_V = 20.75

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
BUTCHER_BLOCK = (190, 172, 76)

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1024 - 32
ALLEY_SCREEN_HEIGHT = SCREEN_HEIGHT
ALLEY_SCREEN_WIDTH = ALLEY_SCREEN_HEIGHT * (LANE_WIDTH / LANE_LENGTH)

# Dimensions
# 480p 9:16 to try and make the window have a similar aspect ratio to the game space alley
# screen_width = 480
# screen_height = 854
# screen_width = LANE_WIDTH * 5
# screen_height = LANE_LENGTH * 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load('assets/bowling-alley.jpg')
clock = pygame.time.Clock()


class BallState(Enum):
    STATIONARY = auto()
    MID_THROW = auto()
    MOVING_IN_LANE = auto()
    OUT_OF_BOUNDS = auto()
    IN_LEFT_GUTTER = auto()
    IN_RIGHT_GUTTER = auto()
    FINISHED = auto()


class Ball:
    """Game logic for the ball - physics, position, etc. in game space"""
    WEIGHT = None
    DIAMETER = 8.5
    RADIUS = DIAMETER / 2
    CIRCUMFERENCE = 2 * math.pi * RADIUS

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.img = BallImage(self)
        self.state = BallState.STATIONARY

    def throw(self, angle, velocity):
        self.state = BallState.MID_THROW
        self.vx = velocity * math.sin(math.radians(angle))
        self.vy = velocity * math.cos(math.radians(angle))
        if False:  # If the ball is thrown behind, ...
            return
        self.state = BallState.MOVING_IN_LANE

    def update(self, dt):
        is_moving_in_lane = self.state == BallState.MOVING_IN_LANE
        has_entered_left_gutter = self.x < LEFT_BOUNDARY - GUTTER_WIDTH / 2
        has_entered_right_gutter = self.x > RIGHT_BOUNDARY + GUTTER_WIDTH / 2
        has_entered_gutter = has_entered_left_gutter or has_entered_right_gutter
        is_finished = self.state == BallState.FINISHED
        in_gutter = self.state == BallState.IN_LEFT_GUTTER or self.state == BallState.IN_RIGHT_GUTTER
        if is_moving_in_lane:
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.y > LANE_LENGTH:  # When the ball reaches the top of the lane, stop it
                self.state = BallState.FINISHED
                self.y = LANE_LENGTH
                # self.on_finish()
            if has_entered_gutter:  # If the ball goes into the gutter, ...
                print(f"GUTTER! x={self.x}")
                if has_entered_left_gutter:
                    self.state = BallState.IN_LEFT_GUTTER
                if has_entered_right_gutter:
                    self.state = BallState.IN_RIGHT_GUTTER
            if False:  # If the ball goes directly out of bounds, ...
                self.state = BallState.OUT_OF_BOUNDS
        if in_gutter:
            self.y += self.vy * dt  # Keep the ball moving vertically in the gutter
            if self.y > LANE_LENGTH:  # When the ball reaches the top of the lane, stop it
                self.state = BallState.FINISHED
                self.y = LANE_LENGTH


class BallImage:
    """Represents the ball's image, which is displayed on the screen, corresponding to self.ball's co-ordinates."""

    RADIUS = Ball.RADIUS * (ALLEY_SCREEN_WIDTH / LANE_WIDTH)
    WIDTH = RADIUS * 2
    HEIGHT = RADIUS * 2

    def __init__(self, ball):
        self.ball = ball
        # self.img = pygame.transform.rotozoom(pygame.image.load('assets/ball_blue_large.png'), 0,0.5)
        # self.width = self.img.get_width()
        # self.height = self.img.get_height()
        self.x = (SCREEN_WIDTH / 2) + (self.WIDTH / 2)
        self.y = SCREEN_HEIGHT - (self.HEIGHT / 2)

    def display(self):
        # print(f"Ball game pos: ({self.ball.x}, {self.ball.y})")
        self.x, self.y = convert_game_to_screen_pos(self.ball.x, self.ball.y)
        # print(f"Ball screen pos: ({self.x}, {self.y})")
        # screen.blit(self.img, (self.x, self.y))
        radius = Ball.RADIUS * (ALLEY_SCREEN_WIDTH / LANE_WIDTH)
        pygame.draw.circle(screen, LIGHT_BLUE, (self.x, self.y), self.RADIUS)


class TrajectoryLine:
    """Represents the trajectory line, which is a line that shows the ball's predicted trajectory."""

    LENGTH = 400

    def __init__(self, ball):
        self.ball = ball
        self.start_pos = None
        self.end_pos = None
        self.__angle = 0
        self.calculate_pos()

    def change_angle(self, angle):
        new_angle = self.__angle + angle
        if -5 <= new_angle <= 5:
            self.__angle = new_angle
            print(self.__angle)
            self.calculate_pos()

    def get_angle(self):
        return self.__angle

    def calculate_pos(self):
        start_x = self.ball.x
        start_y = self.ball.y
        self.start_pos = convert_game_to_screen_pos(start_x, start_y)
        end_x = self.ball.x + self.LENGTH * math.sin(math.radians(self.__angle))
        end_y = self.ball.y + self.LENGTH * math.cos(math.radians(self.__angle))
        self.end_pos = convert_game_to_screen_pos(end_x, end_y)
        # print(f"Angle: {self.__angle}, end_y (game): {end_y}, end_pos (screen): {self.end_pos}")

    def display(self):
        pygame.draw.line(screen, (255, 0, 0), self.start_pos, self.end_pos, 5)


class Pin:
    HEIGHT = 15
    DIAMETER = 4.75
    RADIUS = DIAMETER / 2
    WEIGHT = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = PinImage(self)
        self.hit = False

    def on_hit(self):
        self.hit = True
        print(f"Pin hit at ({self.x}, {self.y})")


class PinImage:
    RADIUS = Pin.RADIUS * (ALLEY_SCREEN_WIDTH / LANE_WIDTH)
    WIDTH = RADIUS * 2
    HEIGHT = RADIUS * 2

    def __init__(self, pin, x=None, y=None):
        self.pin = pin
        self.x = x
        self.y = y

    def display(self):
        self.x, self.y = convert_game_to_screen_pos(self.pin.x, self.pin.y)
        color = RED if self.pin.hit else BLACK
        pygame.draw.circle(screen, color, (self.x, self.y), self.RADIUS)


def return_default_pins():
    h = HALF_PIN_SPACING_H
    v = PIN_SPACING_V
    base_y = FOUL_LINE_TO_FRONT_PIN_DISTANCE
    return [
        Pin(-h * 3, base_y + v * 3), Pin(-h, base_y + v * 3), Pin(h, base_y + v * 3), Pin(h * 3, base_y + v * 3),
        Pin(-h * 2, base_y + v * 2), Pin(0, base_y + v * 2), Pin(h * 2, base_y + v * 2),
        Pin(-h, base_y + v), Pin(h, base_y + v),
        Pin(0, base_y),
    ]

def convert_game_to_screen_pos(game_x, game_y, offset_x=0.0, offset_y=0.0):
    screen_x = SCREEN_WIDTH / 2 + (game_x * (ALLEY_SCREEN_WIDTH / LANE_WIDTH)) + offset_x
    screen_y = ALLEY_SCREEN_HEIGHT - (game_y * (ALLEY_SCREEN_HEIGHT / LANE_LENGTH)) + offset_y
    return screen_x, screen_y


def update_pins(ball, pins):
    for pin in pins:
        pin.img.display()
        if pin.hit:
            continue
        ball_pin_distance = math.sqrt((ball.x - pin.x) ** 2 + (ball.y - pin.y) ** 2)
        # print(f"Ball-pin distance: {ball_pin_distance}")
        if ball_pin_distance < Pin.RADIUS + Ball.RADIUS:
            pin.on_hit()


def on_finish(ball, pins):
    pins_hit = len([1 for pin in pins if pin.hit])
    print(f"Finished! Pins hit: {pins_hit}")
    ball.__init__()  # Reset ball
    pins = return_default_pins()
    return pins

def main():
    ball = Ball()
    trajectory_line = TrajectoryLine(ball)
    pins = return_default_pins()
    running = True
    while running:

        # Fill the screen with a white background
        screen.fill(WHITE)

        # Calculate the alley and gutter dimensions
        left_boundary_x, _ = convert_game_to_screen_pos(LEFT_BOUNDARY, 0)
        right_boundary_x, _ = convert_game_to_screen_pos(RIGHT_BOUNDARY, 0)
        left_gutter_x, _ = convert_game_to_screen_pos(LEFT_BOUNDARY - GUTTER_WIDTH, 0)
        right_gutter_x, _ = convert_game_to_screen_pos(RIGHT_BOUNDARY, 0)
        gutter_width = GUTTER_WIDTH * (ALLEY_SCREEN_WIDTH / LANE_WIDTH)

        # Draw the alley
        pygame.draw.rect(screen, BUTCHER_BLOCK,
                         pygame.Rect(left_boundary_x, 0, ALLEY_SCREEN_WIDTH, ALLEY_SCREEN_HEIGHT))

        # Draw the left gutter
        pygame.draw.rect(screen, BLACK,
                         pygame.Rect(left_gutter_x, 0, gutter_width, ALLEY_SCREEN_HEIGHT))

        # Draw the right gutter
        pygame.draw.rect(screen, BLACK,
                         pygame.Rect(right_gutter_x, 0, gutter_width, ALLEY_SCREEN_HEIGHT))

        # Display the background image
        # screen.blit(background, (0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ball.throw(trajectory_line.get_angle(), 317)
                if event.key == pygame.K_LEFT:
                    trajectory_line.change_angle(-0.5)
                if event.key == pygame.K_RIGHT:
                    trajectory_line.change_angle(0.5)
        if ball.state == BallState.STATIONARY:
            trajectory_line.display()
        if ball.state == BallState.FINISHED:
            pins = on_finish(ball, pins)
        ball.img.display()
        update_pins(ball, pins)
        pygame.display.update()
        dt = clock.tick(FRAMES_PER_SECOND) / 1000.0  # Limits FPS to 60, dt is time in seconds since the last frame
        ball.update(dt)


if __name__ == "__main__":
    main()
