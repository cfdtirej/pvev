from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class EVStat:
    CarID: int = 1
    charge: float = 0.0
    meshcode: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class PostEV:
    time: str
    EV_stat: List[EVStat] = EVStat()


@dataclass
class ChargerProps:
    meshcode: int
    time: str
    ppv: float
    ppv_030: float
    ppv_060: float
    ppv_090: float
    ppv_120: float
    ppv_150: float
    ppv_180: float
    pd: float
    pd_030: float
    pd_060: float
    pd_090: float
    pd_120: float
    pd_150: float
    pd_180: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class ChartjsFmt:
    meshcode: int
    time: List[str]
    ppv: List[float]
    pd: List[float]
    pd_minus_ppv: List[float]
