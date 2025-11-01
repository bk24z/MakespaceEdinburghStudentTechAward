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
    """Represents the bowling ball, which moves, according to its own co-ordinates system."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.img = BallImage(self)
        self.moving = False

    def move(self):
        pass

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
    def __init__(self):
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
                    ball.moving = True
                if event.key == pygame.K_LEFT:
                    trajectory_line.change_angle(-10)
                if event.key == pygame.K_RIGHT:
                    trajectory_line.change_angle(10)
        if ball.moving and ball.img.y >= 150:
            ball.img.y_change = -5
            frame_count += 1
            if frame_count % 1 == 0:  # Only rescale every 10 frames
                ball.img.change_scale(-0.005)
                ball.img.update()
        else:
            ball.img.y_change = 0
        ball.img.y += ball.img.y_change
        ball.img.display()
        if not ball.moving:
            trajectory_line.display()
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
