"""Type stubs for adafruit_ads1x15"""

# Pin constants
P0: int
P1: int
P2: int
P3: int

class ADS1115:
    P0: int
    P1: int
    P2: int
    P3: int
    def __init__(self, i2c, address: int = 0x48): ...

class AnalogIn:
    def __init__(self, ads, pin): ...
    @property
    def value(self) -> int: ...
    @property
    def voltage(self) -> float: ...
