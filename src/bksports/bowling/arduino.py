import time
from enum import Enum

import serial


class ArduinoState(Enum):
    ERROR = -1
    WAITING_FOR_CONNECTION = 0
    PREPARING = 1
    CALIBRATING = 2
    CALIBRATED = 3
    MEASURING = 4
    FINISHED = 5

    @property
    def message(self) -> str:
        return f"{self.name.title()}."


# class ArduinoStateError(Exception):
#     """Exception raised for custom error in the application."""
#
#     MESSAGE
#
#     def __init__(self, value: int) -> None:
#         self.value = value
#         super().__init__(message)
#
#     def __str__(self) -> str:
#         return f"{self.message}"


def get_state(value: int) -> ArduinoState:
    output = next(
        (state for state in list(ArduinoState) if state.value == value),
        ArduinoState.ERROR,
    )
    # if output == ArduinoState.ERROR:
    #     raise ArduinoStateError(
    #         "Invalid state.",
    #     )
    return output


class ArduinoController:
    def __init__(self) -> None:
        self.ser = serial.Serial("/dev/cu.usbmodem0000011", 9600, timeout=1)
        self.state = (
            ArduinoState.WAITING_FOR_CONNECTION
        )  # Undefined, waiting for Arduino input


if __name__ == "__main__":
    # Configure the serial connection
    # Replace 'COM3' with your actual port
    ac = ArduinoController()
    time.sleep(2)  # Wait for connection to establish
    print("Reading live data from Arduino...")
    print()
    try:
        while True:
            if ac.ser.in_waiting > 0:  # Check if data is available
                line = ac.ser.readline().decode("utf-8").rstrip()
                new_state_str, *str_data = line.split(",")
                new_state = get_state(int(new_state_str))
                data = list(map(int, str_data))
                if new_state == ArduinoState.ERROR:
                    print(f"Erroneous input: {line}")
                # print(f"Received: {line}")
                if ac.state != new_state:
                    ac.state = new_state
                    print(ac.state.message)
                if ac.state == ArduinoState.MEASURING:
                    print(data)
                    gyroscope_x, gyroscope_y = data
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        ac.ser.close()  # Always close the port
        print("Serial port closed.")
