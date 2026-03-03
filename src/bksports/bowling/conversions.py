from bksports.constants import (
    ALLEY_SCREEN_LENGTH,
    ALLEY_SCREEN_WIDTH,
    LANE_LENGTH,
    LANE_WIDTH,
    SCREEN_HEIGHT,
)


def convert_game_to_screen_pos(
    game_x: float,
    game_y: float,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
) -> tuple[float, float]:
    """
    Converts a position in game coordinates to the same position in screen coordinates.

    Game coordinates -> origin at the bottom centre of the alley, unit is inches
    Screen coordinates -> origin at the top left of the screen, unit is pixels

    :param game_x: The game x-coordinate (horizontal position on lane).
    :param game_y: The game y-coordinate (distance down the lane).
    :param offset_x: The x-coordinate offset in pixels (if any).
    :param offset_y: The y-coordinate offset in pixels (if any).
    :return: A tuple (screen_x, screen_y) in screen (pixel) coordinates.
    """
    screen_x = (
        ALLEY_SCREEN_LENGTH - (game_y * (ALLEY_SCREEN_LENGTH / LANE_LENGTH)) + offset_x
    )
    screen_y = (
        SCREEN_HEIGHT / 2 - (game_x * (ALLEY_SCREEN_WIDTH / LANE_WIDTH)) + offset_y
    )
    return screen_x, screen_y
