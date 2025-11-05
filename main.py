import pygame
import time
import math
from enum import Enum, auto

pygame.init()

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
background = pygame.image.load('assets/bowling-alley.jpg')
clock = pygame.time.Clock()

FRAMES_PER_SECOND = 60

# Measurements
# All lane, ball, pin measurements are in inches (to align with industry standards)
LANE_WIDTH = 41.5
GUTTER_WIDTH = 9.25
ALLEY_WIDTH = LANE_WIDTH + GUTTER_WIDTH * 2
LANE_LENGTH = 60 * 12  # 60 feet
LEFT_BOUNDARY = -(LANE_WIDTH / 2)
RIGHT_BOUNDARY = (LANE_WIDTH / 2)

PIN_SPACING = 12  # Spacing between centres of pins
PINS = []


class BallState(Enum):
    STATIONARY = auto()
    MID_THROW = auto()
    MOVING_IN_LANE = auto()
    OUT_OF_BOUNDS = auto()
    IN_GUTTER = auto()
    FINISHED = auto()


class Ball:
    """Game logic for the ball - physics, position, etc. in game space"""
    WEIGHT = None
    RADIUS = 8.5 / 2  # ?
    DIAMETER = RADIUS * 2
    CIRCUMFERENCE = 2 * math.pi * RADIUS
    UPDATE_FREQUENCY = 100  # Updates every x seconds

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
        if self.state == BallState.MOVING_IN_LANE:
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.y > LANE_LENGTH:  # When the ball reaches the top of the lane, stop it
                self.state = BallState.FINISHED
                self.y = LANE_LENGTH
            if self.x < LEFT_BOUNDARY or self.x > RIGHT_BOUNDARY:  # If the ball goes into the gutter, ...
                self.state = BallState.IN_GUTTER
            if False:  # If the ball goes directly out of bounds, ...
                self.state = BallState.OUT_OF_BOUNDS
            for pin in PINS:
                if False:  # If the ball hits a pin, ...
                    pass
            print(self.x, self.y)

class BallImage:
    """Represents the ball's image, which is displayed on the screen, corresponding to self.ball's co-ordinates."""

    def __init__(self, ball):
        self.ball = ball
        self.scale = 1
        self.unscaled_img = pygame.image.load('assets/ball_blue_large.png')
        # self.img = pygame.transform.rotozoom(
        #     self.unscaled_img,
        #     0,
        #     self.scale
        # )
        # self.img = self.unscaled_img
        new_size = (self.unscaled_img.get_width() * self.scale,
                    self.unscaled_img.get_height() * self.scale)
        self.img = pygame.transform.scale(self.unscaled_img, new_size)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = (screen_width / 2) - (self.width / 2)
        self.y = 500
        self.x_change = 0
        self.y_change = 0

    def update(self):
        new_size = (self.unscaled_img.get_width() * self.scale,
                    self.unscaled_img.get_height() * self.scale)
        self.img = pygame.transform.scale(self.unscaled_img, new_size)
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def change_scale(self, scale):
        if scale == 0:
            return
        new_scale = self.scale + scale
        if new_scale > 0:
            self.scale = new_scale
            self.update()

    def display(self):
        screen.blit(self.img, (self.x, self.y))


class TrajectoryLine:
    """Represents the trajectory line, which is a line that shows the ball's predicted trajectory."""

    def __init__(self, ball):
        self.ball = ball
        self.start_pos = None
        self.end_pos = None
        self.__angle = 0
        self.calculate_pos()

    def change_angle(self, angle):
        self.__angle += angle
        self.calculate_pos()

    def calculate_pos(self):
        start_pos_x = self.ball.img.x + (self.ball.img.width / 2)
        start_pos_y = self.ball.img.y
        self.start_pos = (start_pos_x, start_pos_y)
        end_pos_x = start_pos_x + 200 * math.sin(math.radians(self.__angle))
        end_pos_y = start_pos_y - 200 * math.cos(math.radians(self.__angle))
        self.end_pos = (end_pos_x, end_pos_y)

    def display(self):
        pygame.draw.line(screen, (255, 0, 0), self.start_pos, self.end_pos, 5)


class Pin:
    HEIGHT = 15
    RADIUS = 1
    DIAMETER = RADIUS * 2
    WEIGHT = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        pass


class PinImage:
    def __init__(self):
        pass


def main():
    ball = Ball()
    trajectory_line = TrajectoryLine(ball)
    running = True
    frame_count = 0
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ball.throw(0, 10)
                if event.key == pygame.K_LEFT:
                    trajectory_line.change_angle(-10)
                if event.key == pygame.K_RIGHT:
                    trajectory_line.change_angle(10)
        if ball.state == BallState.MOVING_IN_LANE and ball.img.y >= 150:
            ball.img.y_change = -5
            frame_count += 1
            if frame_count % 1 == 0:  # Only rescale every 10 frames
                ball.img.change_scale(-0.005)
                ball.img.update()
        else:
            ball.img.y_change = 0
        ball.img.y += ball.img.y_change
        ball.img.display()
        if ball.state == BallState.STATIONARY:
            trajectory_line.display()
        pygame.display.update()
        dt = clock.tick(FRAMES_PER_SECOND) / 1000.0  # Limits FPS to 60, dt is time in seconds since the last frame
        ball.update(dt)


if __name__ == "__main__":
    main()
