from ast import literal_eval
from pathlib import Path
from typing import Dict


with Path(__file__).with_name('windows_zones_data').open() as f:
    windows_zones: Dict[str, str] = literal_eval(f.read())

def get_zoneinfo_name_by_windows_zone(windows_zone: str) -> str:
    return windows_zones.get(windows_zone, windows_zone)

