from .windows_zones_data import windows_zones


def get_zoneinfo_name_by_windows_zone(windows_zone: str) -> str:
    return windows_zones.get(windows_zone, windows_zone)
