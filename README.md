# 🎳 bksports — Motion-Controlled Bowling Simulator

> **Project for the University of Edinburgh Informatics Makerspace Student Technician Award**

## ℹ️ Overview

A 2D top-down bowling simulator built in Python and controlled via IMU sensors connected to an Arduino, designed to be
run on a Raspberry Pi.
Inspired by Wii Sports.

## 🔌 Tech Stack & Prerequisites

### Hardware

- [Arduino Uno R3](https://docs.arduino.cc/hardware/uno-rev3/)
- [Grove IMU 9DOF(lcm20600+AK09918)](https://wiki.seeedstudio.com/Grove-IMU_9DOF-lcm20600+AK09918/)

### Software

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- [Pymunk](https://www.pymunk.org/en/latest/index.html)
- [Pygame](https://www.pygame.org/)

## ⬇️ Installation & Usage

```bash
git clone https://github.com/bk24z/bksports.git # Clone the project
uv sync # Install dependencies
uv run bksports # Start the game
```

## 🤝 Credits

Icons by [Icons8](https://icons8.com/).