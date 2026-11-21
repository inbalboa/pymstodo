from .windows_zones_data import windows_zones


# CLDR keeps legacy IANA names, but modern tzdata ships them only in the optional
# backward/tzdata-legacy package, so ZoneInfo() may fail to find them.
_legacy_iana_zones = {
    'America/Buenos_Aires': 'America/Argentina/Buenos_Aires',
    'America/Godthab': 'America/Nuuk',
    'America/Indianapolis': 'America/Indiana/Indianapolis',
    'Asia/Calcutta': 'Asia/Kolkata',
    'Asia/Katmandu': 'Asia/Kathmandu',
    'Asia/Rangoon': 'Asia/Yangon',
    'Europe/Kiev': 'Europe/Kyiv',
}


def get_zoneinfo_name_by_windows_zone(windows_zone: str) -> str:
    zone = windows_zones.get(windows_zone, windows_zone)
    return _legacy_iana_zones.get(zone, zone)
