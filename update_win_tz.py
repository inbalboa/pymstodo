from pathlib import Path
from urllib.request import urlopen

from defusedxml import ElementTree


ZONES_XML_URL = 'https://raw.githubusercontent.com/unicode-org/cldr/main/common/supplemental/windowsZones.xml'
OUTPUT_FILE = 'pymstodo/windows_zones_data.py'

with urlopen(ZONES_XML_URL) as response:  # noqa: S310
    zones_xml = ElementTree.parse(response)

tz_data = {}
for zone in zones_xml.getroot().find('.//windowsZones/mapTimezones'):
    attrib = zone.attrib
    if attrib['territory'] == '001':
        tz_data[attrib['other']] = attrib['type']

Path(OUTPUT_FILE).write_text(f'windows_zones = {tz_data}\n', encoding='locale')
