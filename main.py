import pygame
import time
import math

pygame.init()

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
background = pygame.image.load('assets/bowling-alley.jpg')
clock = pygame.time.Clock()

class Ball:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.img = BallImage(self)
        self.moving = False
    def move(self):
        pass

class BallImage:
    def __init__(self, ball):
        self.ball = ball
        self.scale = 1
        unscaled_img = pygame.image.load('assets/ball_blue_small.png')
        self.img = pygame.transform.rotozoom(
            unscaled_img,
            0,
            self.scale
        )
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = (screen_width / 2) - (self.width / 2)
        self.y = 500
        self.x_change = 0
        self.y_change = 0
    def display(self):
        screen.blit(self.img, (self.x, self.y))
    def update(self):
        self.img = pygame.transform.rotozoom(self.img, 0, self.scale)

class TrajectoryLine:
    def __init__(self, ball):
        self.angle = 0
        start_pos_x = ball.img.x + (ball.img.width / 2)
        start_pos_y = ball.img.y
        self.start_pos = (start_pos_x, start_pos_y)
        end_pos_x = start_pos_x + 200 * math.sin(math.radians(self.angle))
        end_pos_y = start_pos_y - 200 * math.cos(math.radians(self.angle))
        self.end_pos = (end_pos_x, end_pos_y)
    def change_angle(self, angle):
        self.angle += angle
    def display(self):
        pygame.draw.line(screen, (255, 0, 0), self.start_pos, self.end_pos, 5)

ball = Ball()
trajectory_line = TrajectoryLine(ball)

running = True
frame_count = 0

while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ball.moving = True
            if event.key == pygame.K_LEFT:
                trajectory_line.angle -= 10
            if event.key == pygame.K_RIGHT:
                trajectory_line.angle += 10
    if ball.moving and ball.img.y >= 150:
        ball.img.y_change = -5
        frame_count += 1
        if frame_count % 2 == 0:  # Only rescale every 10 frames
            ball.img.scale -= 0.02
            ball.img.update()
    else:
        ball.img.y_change = 0
    ball.img.y += ball.img.y_change
    ball.img.display()
    if not ball.moving:
        trajectory_line.display()
    pygame.display.update()
    clock.tick(60)