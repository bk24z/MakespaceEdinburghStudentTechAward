import os

import pygame

from bksports.bowling.game import BowlingGame
from bksports.constants import SCREEN_HEIGHT, SCREEN_WIDTH

pygame.init()

# os.environ["SDL_VIDEO_MAC_FULLSCREEN_SPACES"] = "1"
os.environ["SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS"] = "0"  # 0 = off
os.environ["SDL_VIDEO_WINDOW_POS"] = "-1920,0"  # -1920 = secondary on left
os.environ["SDL_VIDEO_FULLSCREEN_DISPLAY"] = "1"  # 1 = secondary
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()


def main() -> None:
    running = True
    while running:
        bowling_game = BowlingGame(screen, clock)
        bowling_game.run()
        running = bowling_game.running
    pygame.quit()


if __name__ == "__main__":
    main()
