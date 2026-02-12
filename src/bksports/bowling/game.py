import math
from enum import Enum, auto

import pygame
import pymunk

import bksports.constants as consts
from bksports.bowling.ball import Ball, BallState
from bksports.bowling.conversions import convert_game_to_screen_pos
from bksports.bowling.pin import Pin, PinSet
from bksports.bowling.score_keeper import ScoreKeeper

# background = pygame.image.load('../../assets/background.jpg')


def setup_bowling_scene(screen: pygame.Surface) -> None:
    """
    Sets up the bowling scene.

    Renders the background, alley, and gutters on the provided screen.

    :param screen: The screen surface where the bowling scene will be drawn.
    """
    # Fill the screen with a white background
    screen.fill(consts.WHITE)
    # Calculate the alley and gutter dimensions
    left_boundary_x, _ = convert_game_to_screen_pos(consts.LEFT_BOUNDARY, 0)
    right_boundary_x, _ = convert_game_to_screen_pos(consts.RIGHT_BOUNDARY, 0)
    left_gutter_x, _ = convert_game_to_screen_pos(
        consts.LEFT_BOUNDARY - consts.GUTTER_WIDTH, 0
    )
    right_gutter_x, _ = convert_game_to_screen_pos(consts.RIGHT_BOUNDARY, 0)
    gutter_width = consts.GUTTER_WIDTH * (consts.ALLEY_SCREEN_WIDTH / consts.LANE_WIDTH)
    # Draw the alley
    pygame.draw.rect(
        screen,
        consts.BUTCHER_BLOCK,
        pygame.Rect(
            left_boundary_x, 0, consts.ALLEY_SCREEN_WIDTH, consts.ALLEY_SCREEN_HEIGHT
        ),
    )
    # Draw the left gutter
    pygame.draw.rect(
        screen,
        consts.BLACK,
        pygame.Rect(left_gutter_x, 0, gutter_width, consts.ALLEY_SCREEN_HEIGHT),
    )
    # Draw the right gutter
    pygame.draw.rect(
        screen,
        consts.BLACK,
        pygame.Rect(right_gutter_x, 0, gutter_width, consts.ALLEY_SCREEN_HEIGHT),
    )


BALL_SCREEN_RADIUS = Ball.RADIUS * (consts.ALLEY_SCREEN_WIDTH / consts.LANE_WIDTH)
BALL_SCREEN_WIDTH = BALL_SCREEN_RADIUS * 2
BALL_SCREEN_HEIGHT = BALL_SCREEN_RADIUS * 2

PIN_SCREEN_RADIUS = Pin.RADIUS * (consts.ALLEY_SCREEN_WIDTH / consts.LANE_WIDTH)
PIN_SCREEN_WIDTH = PIN_SCREEN_RADIUS * 2
PIN_SCREEN_HEIGHT = PIN_SCREEN_RADIUS * 2


class BowlingFrameState(Enum):
    WAITING_FOR_THROW = auto()
    END_OF_FRAME = auto()


class BowlingGame:
    """
    Manages the main flow and functionality of the bowling game.

    Handles rendering the game elements on the screen and manages interactions between the ball, pins, trajectory
    line, and scorekeeper.

    :ivar space: The pymunk Space the game exists in.
    :ivar screen: The Pygame screen Surface used to render the game elements.
    :ivar clock: The Pygame Clock object used to manage frame rate and timekeeping.
    :ivar running: Indicates whether the game is running.
    :ivar frame_state: Indicates the state of the current frame in play.
    :ivar _throw_angle: The angle at which the ball should be thrown at, and that the trajectory line should be at.
    :ivar ball: The ball object used in the game.
    :ivar pin_set: Contains and manages the set of pins in the game.
    :ivar trajectory_line: Displays and calculates the trajectory of the ball based on its angle and position.
    :ivar score_keeper: Keeps track of the game score and manages throws.
    """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        """
        Initialises the bowling game with a defined screen and clock.

        :param screen: The Pygame screen surface used to render the game elements.
        :param clock: The Pygame Clock object used to manage frame rate and timekeeping.
        """
        # Initialise pymunk variables
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        # Intialise pygame variables
        self.screen = screen
        self.clock = clock
        # Intialise game state variables
        self.running = True
        self.frame_state = BowlingFrameState.WAITING_FOR_THROW
        # Initialise game objects
        self.ball = Ball(self.space)
        self.pin_set = PinSet(self.space)
        self.score_keeper = ScoreKeeper()
        # Intialise other game variables
        self._throw_angle = 0.0
        self.tl_start_pos = None
        self.tl_end_pos = None
        # Set trajectory line start and end positions
        self.calculate_trajectory_line_pos()

    @property
    def throw_angle(self) -> float:
        """Returns the value of _throw_angle."""
        return self._throw_angle

    @throw_angle.setter
    def throw_angle(self, value: float) -> None:
        """
        Handles changing the throw angle to a new value.

        Sets the throw angle to a new value, sets the trajectory line's angle to the same value, and
        recalculates the trajectory line's position if that new value is valid (it must be within the range
        -5 to 5 inclusive).

        :param value: The new value for the throw angle.
        """
        if -5 <= value <= 5:
            self._throw_angle = value
            self.calculate_trajectory_line_pos()
        # print(self.throw_angle)
        # print(self.trajectory_line.angle)

    def display_ball(self) -> None:
        """Displays the ball on the screen, at a position relative to its coordinates in the game space."""
        # print(f"Ball game pos: ({self.ball.x}, {self.ball.y})")
        x, y = convert_game_to_screen_pos(self.ball.x, self.ball.y)
        # print(f"Ball screen pos: ({self.x}, {self.y})")
        # screen.blit(self.img, (self.x, self.y))
        pygame.draw.circle(self.screen, consts.LIGHT_BLUE, (x, y), BALL_SCREEN_RADIUS)

    def display_pins(self) -> None:
        """Displays the pins on the screen, at positions relative to their coordinates in the game space."""
        for pin in self.pin_set.pins:
            if pin.removed:
                continue
            x, y = convert_game_to_screen_pos(pin.x, pin.y)
            color = consts.RED if pin.hit else consts.BLACK
            pygame.draw.circle(self.screen, color, (x, y), PIN_SCREEN_RADIUS)

    def calculate_trajectory_line_pos(self) -> None:
        """Calculates and sets the trajectory line's start and end position based on its length and throw angle."""
        length = 400
        start_x = self.ball.x
        start_y = self.ball.y
        self.tl_start_pos = convert_game_to_screen_pos(start_x, start_y)
        end_x = self.ball.x + length * math.sin(math.radians(self.throw_angle))
        end_y = self.ball.y + length * math.cos(math.radians(self.throw_angle))
        self.tl_end_pos = convert_game_to_screen_pos(end_x, end_y)
        # print(f"Angle: {self.__angle}, end_y (game): {end_y}, end_pos (screen): {self.end_pos}")
        # return start_pos, end_pos

    def display_trajectory_line(self) -> None:
        """Displays the trajectory line on the screen, at its calcuated start and end positions."""
        pygame.draw.line(
            self.screen, (255, 0, 0), self.tl_start_pos, self.tl_end_pos, 5
        )

    def handle_waiting_for_throw_state(self) -> None:
        """Handles logic and pygame rendering when the game is waiting for the user to make a throw."""
        # Set up scene
        setup_bowling_scene(self.screen)
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.ball.throw(self.throw_angle, 317.0)
                elif event.key == pygame.K_LEFT:
                    self.throw_angle -= 0.5
                elif event.key == pygame.K_RIGHT:
                    self.throw_angle += 0.5

    def handle_end_of_throw_state(self) -> None:
        """Handles logic and pygame rendering when the current throw has just ended."""
        print(f"Pins hit: {self.pin_set.pins_hit}")
        # If the frame has now finished after this throw
        if self.score_keeper.add_throw(self.pin_set.pins_hit):
            self.pin_set = PinSet(self.space)  # Reset pins
            print(self.score_keeper)  # Show current game state TODO: Display on screen
            self.frame_state = BowlingFrameState.END_OF_FRAME
        else:
            self.pin_set.clean_up()  # Remove knocked pins
        self.ball = Ball(self.space)  # Reset ball
        self.throw_angle = 0  # Reset throw angle
        self.pin_set.pins_hit = 0

    def handle_end_of_frame_state(self) -> None:
        """Handles logic and pygame rendering when the current frame has ended."""
        self.screen.fill(consts.WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.frame_state = BowlingFrameState.WAITING_FOR_THROW
        pygame.display.update()
        self.space.step(1 / consts.FRAMES_PER_SECOND)

    def handle_finished_game(self) -> None:
        self.screen.fill(consts.BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
            ):
                self.running = False
        pygame.display.update()
        self.space.step(1 / consts.FRAMES_PER_SECOND)

    def run(self) -> None:
        """
        Executes the main game loop.

        Loops through listening for keystroke events, displaying elements on screen, and updating game state
        accordingly while the game is running. Also limits the game to run at 60fps.
        """
        while self.running:
            # If the game is finished
            if self.score_keeper.finished:
                self.handle_finished_game()
            # If the game is waiting for the player to throw the ball
            elif self.frame_state == BowlingFrameState.WAITING_FOR_THROW:
                self.handle_waiting_for_throw_state()
                if self.ball.state == BallState.STATIONARY:
                    self.display_trajectory_line()
                elif self.ball.state == BallState.FINISHED:
                    self.handle_end_of_throw_state()
                # Update ball state
                self.ball.update()
                # Display ball and pins
                self.display_ball()
                self.display_pins()
                pygame.display.update()
                # Limit FPS to 60, and updates per frame to 1/60
                self.clock.tick(consts.FRAMES_PER_SECOND)
                self.space.step(1 / consts.FRAMES_PER_SECOND)
            # If the current frame has ended
            elif self.frame_state == BowlingFrameState.END_OF_FRAME:
                self.handle_end_of_frame_state()
