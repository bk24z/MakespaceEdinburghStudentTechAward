import math
import random
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

    MASS = 6.8  # kg
    DIAMETER = 8.595  # inches
    RADIUS = DIAMETER / 2  # inches
    CIRCUMFERENCE = 2 * math.pi * RADIUS  # inches

    def __init__(self, space: pymunk.Space) -> None:
        """
        Intialises the ball and adds it to the pymunk Space.

        :param space: The pymunk Space the game exists in.
        """
        self.state = BallState.STATIONARY
        self.body = pymunk.Body()
        self.body.position = (
            random.uniform(
                -0.5,
                0.5,
            ),  # Slightly random x-coord to avoid throwing directly straight every time
            0,
        )
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.mass = self.MASS
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

    @x.setter
    def x(self, value: float) -> None:
        """
        Handles changing the x-coordinate of the ball's current position to a new value.

        Sets the ball's x-coordinate to a new value if that new value is valid (it must be within the range
        of the left and right boundary values inclusive) and the ball is stationary.

        :param value: The new value for the ball's x-coordinate.
        """
        if (
            consts.LEFT_BOUNDARY <= value <= consts.RIGHT_BOUNDARY
            and self.state == BallState.STATIONARY
        ):
            self.body.position = (value, self.y)
        # elif value < consts.LEFT_BOUNDARY:
        #     self.body.position = (consts.LEFT_BOUNDARY, self.y)
        # elif value > consts.RIGHT_BOUNDARY:
        #     self.body.position = (consts.RIGHT_BOUNDARY, self.y)

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

    @property
    def speed(self) -> float:
        """Returns the speed of the ball, by using Pythogoras on the x and y components of the ball's velocity."""
        return self.body.velocity.length

    @property
    def angle_of_movement(self) -> float:
        """Returns the angle between the x and y components of the ball's velocity, in degrees."""
        return self.body.velocity.angle_degrees

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
            if self.y > consts.LANE_LENGTH + 100:
                self.state = BallState.FINISHED
            # If the ball passes a lane boundary
            elif has_entered_gutter:
                # If the ball goes directly out of bounds
                if (
                    self.vy / abs(self.vx) < 10 and self.speed > 500
                ):  # TODO: Tweak values
                    # self.state = BallState.OUT_OF_BOUNDS
                    pass
                else:
                    print(f"GUTTER! x={self.x}")
                    self.body.velocity = (0, self.vy)
                    if has_entered_left_gutter:
                        self.state = BallState.IN_LEFT_GUTTER
                    if has_entered_right_gutter:
                        self.state = BallState.IN_RIGHT_GUTTER
        if (
            in_gutter
            and self.y
            > consts.LANE_LENGTH + 100  # 100 = buffer to allow for chain reactions
        ):  # When the ball reaches the top of the lane, stop it
            self.state = BallState.FINISHED
