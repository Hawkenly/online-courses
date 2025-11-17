from dataclasses import dataclass
from typing import Optional

@dataclass
class WeatherRequestDto:
    lat: Optional[float] = None
    lon: Optional[float] = None

@dataclass
class WeatherResponseDto:
    temperature: float
    windspeed: float
    winddirection: float
    time: str

