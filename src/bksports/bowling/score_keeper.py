class ScoreKeeper:
    """
    Handles the scoring system for the bowling game.

    :ivar frames: List of integer lists storing the individual throws within each frame.
    :ivar frame_start_indexes: List storing the flattened index of the starting throw for each frame in `frames`.
    :ivar current_frame: List of integers storing the throws of the current frame being played.
    :ivar current_frame_num: The (zero-indexed) number of the current frame being played.
    :ivar game_finished: Boolean indicating whether the game has finished (the 10th frame has ended).
    """

    def __init__(self) -> None:
        """Initialises the ScoreKeeper object."""
        self.frames: list[list[int]] = []
        self.frame_start_indexes: list[int] = []
        self.current_frame: list[int] = []
        self.current_frame_num: int = 0
        self.game_finished: bool = False

    @property
    def all_throws(self) -> list[int]:
        """Flattens the `frames` list into a 1D list of all throws."""
        return [throw for frame in self.frames for throw in frame]

    def _end_frame(self) -> None:
        """Helper function for `add_throw`. Ends the current frame and starts a new frame."""
        self.frames.append(self.current_frame)
        self.frame_start_indexes.append(
            len(self.all_throws) - len(self.current_frame),
        )
        self.current_frame = []
        self.current_frame_num += 1

    def add_throw(self, throw: int) -> bool:
        """
        Adds a throw and its score to the current frame.

        Determines if the throw completes the current frame or if further throws are needed.
        Handles special cases for strikes, spares, and the final frame.

        :param throw: The score of the current throw to be added.
        :return: True if the current frame has been completed, otherwise False.
        """
        if (
            self.current_frame_num < 9 and len(self.current_frame) < 2
        ):  # Unfinished 1st-9th frame
            if throw == 10 and len(self.current_frame) == 0:  # Strike
                self.current_frame.append(throw)
                self._end_frame()
                return True  # Current frame has ended
            self.current_frame.append(throw)
            if len(self.current_frame) == 2:  # Spare or score less than 10
                self._end_frame()
                return True
        if self.current_frame_num == 9:  # 10th frame
            if len(self.current_frame) == 0:  # First throw in 10th frame
                self.current_frame.append(throw)
                return False
            if (
                self.current_frame[0] == 10 and len(self.current_frame) < 3
            ):  # First throw was a strike
                self.current_frame.append(throw)
                if len(self.current_frame) == 3:  # 3 throws = end of frame and game
                    self._end_frame()
                    self.game_finished = True
                    return True
            elif len(self.current_frame) < 3:
                self.current_frame.append(throw)
                if (
                    len(self.current_frame) == 2 and sum(self.current_frame) < 10
                ):  # 2 throws, no spare
                    self._end_frame()
                    self.game_finished = True
                    return True
                if len(self.current_frame) == 3:
                    self._end_frame()
                    self.game_finished = True
                    return True

        return False  # Current frame has not ended

    def add_throws(self, throws: list[int]) -> bool:
        """
        Adds a list of throws to their respective frames by running `add_throw` on each throw.

        :param throws: A list of integers representing the throws to be added.
        :return: True if the last throw completed its frame, otherwise False.
        """
        status = False
        for throw in throws:
            status = self.add_throw(throw)
        return status

    def get_score(self, frame_num: int) -> int:
        """
        Calculates the cumulative score of the game at a specific frame number.

        If a frame is incomplete or the necessary bonus points for a strike or a spare are
        unavailable, the method returns -1 to indicate the frame's score cannot
        yet be determined.

        :param frame_num: The (zero-indexed) frame number at which the score should be calculated.
        :return: The cumulative score at the given frame, or -1 if it cannot yet be calculated.
        """
        score = 0
        for i in range(frame_num + 1):
            frame = self.frames[i]
            try:
                next_frame_start = self.frame_start_indexes[i + 1]
            except IndexError:
                next_frame_start = None
            frame_sum = sum(frame)
            score += min(frame_sum, 30)  # Max score of 30 in one frame
            if frame_sum < 10:  # Not strike or spare, 1st-9th frame
                continue
            if i == 9:  # 10th frame
                if len(frame) < 3:
                    return -1  # Frame isn't finished
                if len(frame) == 3:
                    return score
            if frame_sum == 10:  # Strike or spare, 1st-9th frame
                try:
                    if len(frame) == 1:  # Strike, 1st-9th frame
                        if next_frame_start is None:
                            return -1  # Waiting for next throws
                        bonus = self.all_throws[next_frame_start : next_frame_start + 2]
                        if len(bonus) < 2:
                            return -1
                        score += sum(bonus)
                    elif len(frame) == 2:  # Spare, 1st-9th frame
                        if next_frame_start is None:
                            return -1  # Waiting for next throws
                        bonus = self.all_throws[next_frame_start : next_frame_start + 1]
                        if len(bonus) < 1:
                            return -1
                        score += sum(bonus)
                except IndexError:
                    return -1  # Waiting for next throws
        return score

    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        Details for each frame, the throws made in it, and its current cumulative score.

        :return: A formatted string displaying the details for each frame.
        """
        result = "\n"
        frame_score = 0
        for i, frame in enumerate(self.frames):
            frame_score = self.get_score(frame_num=i)
            if frame_score == -1:
                result += f"Frame {i + 1}:\n{frame} Uncalculated, more throws needed to calculate\n"
                break
            result += f"Frame {i + 1}:\n{frame} {frame_score}\n"
        result += (
            f"\nFinal score: {frame_score}"
            if self.game_finished
            else "\nGame not finished"
        )
        return result

    def test_setup(self) -> None:
        """
        Sets up a test game scenario for debugging and testing.

        Uses the example game from this article:
        https://bowlingforbeginners.com/how-is-bowling-scored/
        """
        self.add_throws([6, 2])
        self.add_throws([10])
        self.add_throws([3, 2])
        self.add_throws([5, 5])
        self.add_throws([10])
        self.add_throws([10])
        self.add_throws([1, 4])
        self.add_throws([9, 0])
        self.add_throws([3, 2])
        self.add_throws([10, 10, 10])
        print(self)


if __name__ == "__main__":
    sk = ScoreKeeper()
    sk.test_setup()
