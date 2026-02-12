import math
from enum import Enum, auto

import pymunk

import bksports.constants as consts


class BallState(Enum):
    STATIONARY = auto()
    MID_THROW = auto()
    MOVING_IN_LANE = auto()
    OUT_OF_BOUNDS = auto()
    IN_LEFT_GUTTER = auto()
    IN_RIGHT_GUTTER = auto()
    FINISHED = auto()


class Ball:
    """
    Represents a bowling ball and its attributes, including its physics, position, and state within the game space.

    :ivar MASS: The weight of the ball (currently undefined).
    :ivar DIAMETER: The diameter of the ball.
    :ivar RADIUS: The radius of the ball, derived from its diameter.
    :ivar CIRCUMFERENCE: The circumference of the ball, derived from its radius.
    :ivar state: The current state of the ball, which is an instance of the BallState enum.
    :ivar body: The pymunk Body of the pin.
    :ivar shape: The pymunk Shape of the pin.
    """

    MASS = 10  # kg
    DIAMETER = 8.5  # inches
    RADIUS = DIAMETER / 2  # inches
    CIRCUMFERENCE = 2 * math.pi * RADIUS  # inches

    def __init__(self, space: pymunk.Space) -> None:
        """
        Intialises the ball and adds it to the pymunk Space.

        :param space: The pymunk Space the game exists in.
        """
        self.state = BallState.STATIONARY
        self.body = pymunk.Body()
        self.body.position = (0, 0)
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.mass = (
            self.MASS
        )  # TODO: Change value / add ball choice functionality
        self.shape.elasticity = 0.9
        self.shape.friction = 0.4
        self.shape.collision_type = (
            consts.BALL_ID  # Assign collision type ID 0 to the ball
        )
        space.add(self.body, self.shape)

    @property
    def x(self) -> float:
        """Returns the x-coordinate of the ball's current position."""
        return self.body.position.x

    @property
    def y(self) -> float:
        """Returns the y-coordinate of the ball's current position."""
        return self.body.position.y

    @property
    def vx(self) -> float:
        """Returns the x-component of the ball's current velocity."""
        return self.body.velocity.x

    @property
    def vy(self) -> float:
        """Returns the y-component of the ball's current velocity."""
        return self.body.velocity.y

    def throw(self, angle: float, velocity: float) -> None:
        """
        Throw the ball in the given direction with the given velocity.

        :param angle: The angle in degrees the ball is thrown at, relative to the vertical.
        :param velocity: The velocity of the ball in inches per second.
        """
        self.state = BallState.MID_THROW
        if False:  # If the ball is thrown behind, ...
            return
        vx = velocity * math.sin(math.radians(angle))
        vy = velocity * math.cos(math.radians(angle))
        impulse_x = self.body.mass * vx
        impulse_y = self.body.mass * vy
        self.body.apply_impulse_at_local_point((impulse_x, impulse_y), (0, 0))
        self.state = BallState.MOVING_IN_LANE

    def update(self) -> None:
        """Update the ball's state based on its position."""
        is_moving_in_lane = self.state == BallState.MOVING_IN_LANE
        has_entered_left_gutter = (
            self.x < consts.LEFT_BOUNDARY - consts.GUTTER_WIDTH / 2
        )
        has_entered_right_gutter = (
            self.x > consts.RIGHT_BOUNDARY + consts.GUTTER_WIDTH / 2
        )
        has_entered_gutter = has_entered_left_gutter or has_entered_right_gutter
        is_finished = self.state == BallState.FINISHED
        in_gutter = self.state in (BallState.IN_LEFT_GUTTER, BallState.IN_RIGHT_GUTTER)
        if is_moving_in_lane:
            # When the ball reaches the top of the lane, stop it
            if self.y > consts.LANE_LENGTH:
                self.state = BallState.FINISHED
                # self.y = consts.LANE_LENGTH
                # self.on_finish()
            # If the ball goes into the gutter, ...
            if has_entered_gutter:
                print(f"GUTTER! x={self.x}")
                self.body.velocity = (0, self.y)
                if has_entered_left_gutter:
                    self.state = BallState.IN_LEFT_GUTTER
                if has_entered_right_gutter:
                    self.state = BallState.IN_RIGHT_GUTTER
            # If the ball goes directly out of bounds, ...
            if False:
                self.state = BallState.OUT_OF_BOUNDS
        if in_gutter:
            # self.y += self.vy * dt  # Keep the ball moving vertically in the gutter
            if (
                self.y > consts.LANE_LENGTH
            ):  # When the ball reaches the top of the lane, stop it
                self.state = BallState.FINISHED
                # self.y = consts.LANE_LENGTH
