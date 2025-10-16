"""Type stubs for Adafruit CircuitPython libraries"""

class ServoKit:
    def __init__(self, channels: int = 16, address: int = 0x40): ...
    servo: list

class PCA9685:
    def __init__(self, i2c, address: int = 0x40): ...
