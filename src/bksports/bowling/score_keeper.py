class ScoreKeeper:
    """
    Handles the scoring system for the bowling game.

    :ivar raw_score_data: The list of individual scores for each throw. Contains `None` for incomplete scores.
    :ivar frame_indexes: Set of indexes marking the start of each frame within the scores list.
    :ivar frame_throws: List containing sublists, where each one represents the throws of a single frame.
    :ivar current_frame_throws: The list of throws for the frame that is currently being played.
    """

    def __init__(self) -> None:
        """Initialises the scorekeeper object."""
        self.raw_score_data: list[int | None] = []
        self.frame_indexes: set[int] = set()
        self.frame_throws: list[list[int]] = []
        self.current_frame_throws: list[int] = []
        self.finished: bool = False

    @property
    def is_last_frame(self) -> bool:
        """
        Checks if the current frame will be the last frame of the game.

        It does this by checking if the number of frames is equal to 10 (the standard number of frames in a bowling
        game).

        :return: True if the number of frames is equal to 9, otherwise False.
        """
        return len(self.frame_score_data) == 10

    @property
    def valid_scores(self) -> list[int]:
        """
        Returns the scores list but with any None values filtered out and not included.

        :returns: A list containing all scores from self.scores that are not None.
        """
        return [score for score in self.raw_score_data if score is not None]

    @property
    def total_score(self) -> int:
        """
        Returns the total score of the game by summing the list of valid scores.

        :return: The sum of self.valid_scores.
        """
        return sum(self.valid_scores)

    @property
    def frame_score_data(self) -> list[list[int]]:
        """
        Returns the list of frames.

        Slices the scores list by the starting positions of each frame defined in the frame_starts list.

        :return: A list containing sublists, with each sublist representing a frame.
        """
        result = []
        sorted_frame_starts = sorted(self.frame_indexes)
        prev_frame_start = sorted_frame_starts[0]
        for frame_start in sorted_frame_starts[1:]:
            result.append(self.raw_score_data[prev_frame_start:frame_start])
            prev_frame_start = frame_start
        result.append(self.raw_score_data[prev_frame_start:])
        return result

    @property
    def frame_totals(self) -> list[int | None]:
        """
        Calculates the total score for each frame.

        If a frame contains any None values (indicating that it is incomplete), the corresponding score will also have
        a value of None. Otherwise, the sum of the frame's scores will be calculated.

        :return: A list containing the total scores (or None values) for each frame.
        """
        return [
            sum(frame) if None not in frame else None for frame in self.frame_score_data
        ]

    def add_throw(self, score: int) -> bool:
        """
        Add a throw and its score to the current frame.

        Determines if the throw completes the current frame or if further throws are needed.
        Handles special cases for strikes, spares, and the final frame.

        :param score: The score of the current throw to be added.
        :return: True if the current frame has been completed, otherwise False.
        """
        # Get and add the frame's index to the frame_indexes list
        if len(self.frame_indexes) < 10:
            frame_index = len(self.raw_score_data)
            self.frame_indexes.add(frame_index)
        # Add the throw to the current frame's throws
        self.current_frame_throws.append(score)

        def check_throw() -> bool:
            """
            Helper function for add_throw().

            Handles special cases (strike/spare/final frame), adds the throw's score to the current frame, and ends
            the frame when necessary.

            :return: True if the current frame has been completed, otherwise False.
            """
            # If this throw is in the last frame
            if self.is_last_frame:
                # If the number of strikes in this frame (including this throw) is 2 or less
                if score == 10 and len(self.current_frame_throws) <= 2:
                    self.end_open_frame([10])
                    return False  # The final frame has not finished at this point
                # If the current throw is the 2nd throw in the frame
                # Either a spare or an open frame
                non_10_throws = [
                    throw for throw in self.current_frame_throws if throw != 10
                ]
                if len(non_10_throws) == 2:
                    if sum(non_10_throws) == 10:
                        self.end_spare_frame(non_10_throws)
                        return True
                    else:
                        self.end_open_frame(non_10_throws)
                        return True  # The final frame has now finished
                # If this throw is the 3rd throw in this frame
                if len(self.current_frame_throws) == 3:
                    self.end_open_frame(
                        [score]
                    )  # Add the score of the last (current) throw to the frame
                    return True  # The final frame has now finished
            # If this throw is not in the last frame
            elif self.current_frame_throws == [10]:  # If this throw is a strike
                self.end_strike_frame()
                return True  # This frame has now ended
            elif (
                len(self.current_frame_throws) == 2
            ):  # If this throw leaves a spare or open frame
                if sum(self.current_frame_throws) == 10:  # If this throw leaves a spare
                    self.end_spare_frame(self.current_frame_throws)
                else:  # If the throw leaves an open frame
                    self.end_open_frame(self.current_frame_throws)
                return True  # This frame has now ended
            return False

        frame_complete = check_throw()
        if frame_complete:
            self.frame_throws.append(self.current_frame_throws)
            self.current_frame_throws = []  # Clear current throws if the frame is complete
            if self.is_last_frame:
                # Adjust each frame to make sure they don't exceed the limit of 30
                for frame in self.frame_score_data:
                    frame_total = sum(frame)
                    if frame_total > 30:
                        self.raw_score_data.append(30 - frame_total)
                # Mark that the game is finished
                self.finished = True
        return frame_complete

    def add_throws(self, throws: list[int]) -> bool:
        """
        Adds a list of throws to their respective frames by running add_throw on each throw.

        :param throws: A list of integers representing the throws to be added.
        :return: True if the last throw completed its frame, otherwise False.
        """
        status = False
        for throw in throws:
            status = self.add_throw(throw)
        return status

    def end_open_frame(self, frame: list[int]) -> None:
        """
        Ends the provided open frame.

        Calculates any uncalculated scores from previous strikes and spares, and saving the frame's scores to the list
        of scores.

        :param frame: The list of integers representing the scores for each throw in a frame.
        """
        self.calc_strikes_and_spares(frame)
        self.raw_score_data.extend(frame)

    def end_spare_frame(self, frame: list[int]) -> None:
        """
        Ends the provided spare frame.

        Calculates any uncalculated scores from previous strikes and spares, and saving the frame's scores, alongside
        an extra None value to account for the next throw, to the list of scores.

        :param frame: The list of integers representing the scores for each throw in a frame.
        """
        self.calc_strikes_and_spares(frame)
        self.raw_score_data.extend([*frame, None])

    def end_strike_frame(self) -> None:
        """
        Ends a strike frame.

        Calculates any uncalculated scores from previous strikes and spares, and saving a single 10 score, alongside
        two extra None values to account for the next two throws, to the scores list.
        """
        self.calc_strikes_and_spares([10])
        self.raw_score_data.extend([10, None, None])

    def calc_strikes_and_spares(self, frame: list[int]) -> None:
        """
        Calculates and updates any uncalculated scores from strikes and spares, using the current frame.

        If the frame list does not supply enough values, it uses the value of the last non-None score to fill the
        missing scores.

        :param frame: The list of integers representing the scores for each throw in a frame.
        """
        frame = frame.copy()
        while None in self.raw_score_data:
            n_index = (
                len(self.raw_score_data) - 1 - self.raw_score_data[::-1].index(None)
            )
            if frame:
                self.raw_score_data[n_index] = frame.pop()
            else:
                # TODO: Check that this logic is correct with more examples
                # print(self.scores[-2])
                self.raw_score_data[n_index] = self.raw_score_data[-2]
                break
        # print(self.scores)

    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        Details for each frame, the throws made in it and its current cumulative score.

        :return: A formatted string displaying the details for each frame.
        """
        result = "\n"
        c_score = 0
        for i, frame in enumerate(self.frame_score_data):
            if None not in frame:
                # TODO: Maybe optimise current score calculation to be more efficient
                c_score += sum([score for score in frame if score is not None])
                result += f"Frame {i + 1}:\n{self.frame_throws[i]} {c_score}\n"
            else:
                result += f"Frame {i + 1}:\n{self.frame_throws[i]} Uncalculated, more throws needed to calculate\n"
                break
        result += (
            f"\nFinal score: {c_score}" if self.finished else "\nGame not finished"
        )
        return result

    def test_setup(self) -> None:
        self.add_throws([6, 2])
        self.add_throws([10])
        self.add_throws([3, 2])
        self.add_throws([5, 5])
        self.add_throws([10])
        self.add_throws([10])
        self.add_throws([1, 4])
        self.add_throws([9, 0])
        self.add_throws([3, 2])
        print(self.add_throws([10, 10, 1]))
        print(self.raw_score_data, self.total_score)
        print(self.frame_indexes)
        print(self.frame_score_data)
        print(self.frame_throws)
        print(self)


# Example game - https://bowlingforbeginners.com/how-is-bowling-scored/
if __name__ == "__main__":
    sk = ScoreKeeper()
    sk.test_setup()
