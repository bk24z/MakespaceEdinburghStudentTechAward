import time
from enum import Enum

import serial


class ArduinoState(Enum):
    ERROR = -1
    WAITING = 0
    CONNECTED = 1
    MEASURING = 2

    @property
    def message(self) -> str:
        """Returns a message describing the current state."""
        match self:
            case ArduinoState.WAITING:
                return "Not connected. Waiting for connection..."
            case _:
                return f"{self.name.title()}."


def get_state(value: int) -> ArduinoState:
    output = next(
        (state for state in list(ArduinoState) if state.value == value),
        ArduinoState.ERROR,
    )
    return output


class ArduinoController:
    def __init__(self) -> None:
        self.state = ArduinoState.WAITING  # Waiting for Arduino input
        try:
            self.ser = serial.Serial("/dev/cu.usbmodem0000011", 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino to start up
            self.connect_to_serial()
        except serial.SerialException:
            self.state = ArduinoState.ERROR
            print(
                "Arduino is not connected. Connect Arduino and press C in the game window to retry connecting.",
            )

    def close(self) -> None:
        """Closes the Arduino serial port."""
        self.ser.close()
        self.state = ArduinoState.WAITING
        print("Serial port closed.")

    def is_connected(self) -> bool:
        """
        Determines if the serial connection is currently active (connecting raises no errors).

        :return: True if the serial connection is active, otherwise False.
        """
        if not hasattr(self, "ser"):
            return False
        try:
            _ = self.ser.in_waiting
        except serial.SerialException:
            return False
        else:
            return True

    def connect_to_serial(self) -> None:
        """
        Establishes connection to Arduino and prepares the program to read its serial port.

        :raises KeyboardInterrupt: If the user interrupts the connection process.
        """
        self.state = ArduinoState.WAITING
        try:
            while self.state != ArduinoState.CONNECTED:
                if self.ser.in_waiting > 0:  # Check if data is available
                    line = self.ser.readline().decode("utf-8").rstrip()
                    new_state_str = line.split(",")[0]
                    self.state = get_state(int(new_state_str))
        except KeyboardInterrupt:
            print("\nProgram stopped by user.")
            self.close()
            return
        finally:
            print(self.state.message)

    def readline(self) -> tuple[int, ...]:
        """
        Reads and decodes a single line of data from the serial input, and updates state accordingly.

        :return: A tuple containing integers extracted from the decoded data.
        :rtype: tuple[int, ...]
        """
        line = self.ser.readline().decode("utf-8").rstrip()
        new_state_str, *str_data = line.split(",")
        self.state = get_state(int(new_state_str))
        data = tuple(map(float, str_data))
        # print(self.state.message, data)
        if self.state != ArduinoState.ERROR:
            self.state = ArduinoState.CONNECTED
        return data


if __name__ == "__main__":
    ac = ArduinoController()
    is_connected = ac.is_connected()
    print(is_connected)
    if is_connected:
        input("Press Enter to read")
        end_time = time.time() + 10
        while time.time() < end_time:
            print(ac.readline())
            ac.ser.reset_input_buffer()
