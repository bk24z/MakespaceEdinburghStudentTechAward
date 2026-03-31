import time
from collections.abc import Callable
from enum import Enum

import serial


class ArduinoState(Enum):
    ERROR = -1
    CONNECTING = 0
    CONNECTED = 1
    MEASURING = 2
    FINISHED = 3

    @property
    def message(self) -> str:
        return f"{self.name.title()}."


def get_state(value: int) -> ArduinoState:
    output = next(
        (state for state in list(ArduinoState) if state.value == value),
        ArduinoState.ERROR,
    )
    return output


# def calculate_ball_speed(
#     gyroscope_x_data: list[int], gyroscope_y_data: list[int],
# ) -> float:
#     gyroscope_x_max, gyroscope_y_max = max(g_x_data), max(g_y_data)
#     return gyroscope_y_max


class ArduinoController:
    def __init__(self) -> None:
        self.state = ArduinoState.CONNECTING  # Waiting for Arduino input
        self.ser = serial.Serial("/dev/cu.usbmodem0000011", 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to start up
        self.connect()

    def connect(self) -> None:
        """
        Establishes connection to Arduino and prepares the program to read its serial port.

        :raises KeyboardInterrupt: If the user interrupts the connection process.
        """
        try:
            while self.state != ArduinoState.CONNECTED:
                if self.ser.in_waiting > 0:  # Check if data is available
                    line = self.ser.readline().decode("utf-8").rstrip()
                    new_state_str, *str_data = line.split(",")
                    self.state = get_state(int(new_state_str))
        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
            self.ser.close()
            return
        finally:
            print(self.state.message)

    def read(self, condition: Callable[[], bool]) -> tuple[list[int], list[int]]:
        """
        Reads serial data while a specific condition is met and returns the data measured in this period.

        :param condition: A boolean-returning function, indicating whether the read operation should continue.
        :return: A tuple containing the lists of data. (gyroscope_x_data, gyroscope_y_data)
        """
        if not self.ser.is_open:
            print("Reopening serial port...")
            self.ser.open()
            time.sleep(2)
        gyroscope_x_data = []
        gyroscope_y_data = []
        data_lists = (gyroscope_x_data, gyroscope_y_data)
        try:
            while self.ser.in_waiting <= 0:
                time.sleep(0.1)
            while condition():
                if self.ser.in_waiting > 0:  # Check if data is available
                    line = self.ser.readline().decode("utf-8").rstrip()
                    new_state_str, *str_data = line.split(",")
                    self.state = get_state(int(new_state_str))
                    data = list(map(int, str_data))
                    print(self.state.message, data)
                    for i, p in enumerate(data):
                        data_lists[i].append(p)
        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
        finally:
            self.ser.close()
        return data_lists


if __name__ == "__main__":
    ac = ArduinoController()
    input("Press Enter to read")
    end_time = time.time() + 10
    g_x_data, g_y_data = ac.read(lambda: time.time() < end_time)
    print(max(g_x_data), max(g_y_data))
