# Leaflet cluster map of talk locations
#
# Run this from the repository root. It reads the Markdown front matter from
# _talks/*.md, geolocates each talk location with geopy/Nominatim, and writes the
# standalone cluster map into talkmap/.
import glob
import re

import getorg
import yaml
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

TIMEOUT = 5

# Collect the Markdown files
g = glob.glob("_talks/*.md")

# Prepare to geolocate
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}

for file in g:
    with open(file, "r", encoding="utf-8") as fh:
        text = fh.read()

    if not text.startswith("---\n"):
        continue

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        continue

    try:
        data = yaml.safe_load(parts[0][4:])
    except Exception:
        continue

    if not isinstance(data, dict) or "location" not in data:
        continue

    title = str(data.get("title", "")).strip()
    venue = str(data.get("venue", "")).strip()
    location = str(data.get("location", "")).strip()
    if not title or not venue or not location:
        continue

    description = f"{title}<br />{venue}; {location}"
    geocode_location = re.sub(r"\s*\([^)]*\)\s*", " ", location).strip()
    if not geocode_location:
        continue

    try:
        result = geocoder.geocode(geocode_location, timeout=TIMEOUT)
        if result is None:
            print(f"Error: geocode returned no result for input {geocode_location}")
            continue
        location_dict[description] = result
        print(description, result)
    except ValueError as ex:
        print(f"Error: geocode failed on input {geocode_location} with message {ex}")
    except GeocoderTimedOut as ex:
        print(f"Error: geocode timed out on input {geocode_location} with message {ex}")
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {geocode_location} with message {ex}")

m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(location_dict, folder_name="talkmap", hashed_usernames=False)
