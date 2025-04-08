# https://www.kaggle.com/code/chandancharchitsahoo/visualize-maps-using-folium
# https://www.kaggle.com/datasets/tapakah68/yandextoloka-water-meters-dataset
# todo next steps create separate script for generating map
#   one for generating initial data
#   one for generating map


import pandas as pd
import requests
import folium
import webbrowser
import random
from shapely.geometry import shape, Point, MultiPolygon
from folium import plugins
from datetime import datetime, timedelta

def get_random_meter_value(min_val=1000.0, max_val=8000.0, precision=2):
    return round(random.uniform(min_val, max_val), precision)

def get_random_date_and_epoch():
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = start_date + timedelta(days=random_days)
    formatted_date = random_date.strftime('%Y-%m-%d')
    epoch = int(random_date.timestamp())
    return formatted_date, epoch

def generate_serial_number(length=10):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def get_zip_from_point(lat, lon, crescenta_boundaries):
    point = Point(lon, lat)  # shapely uses (x=lon, y=lat)
    for feature in crescenta_boundaries["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            return feature["properties"]["ZCTA5CE10"]
    return None  # Not found in any polygon


# Get Crescenta Valley boundary as GeoJSON (approximate boundaries)
boundary_url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/ca_california_zip_codes_geo.min.json"
response = requests.get(boundary_url)
geojson_data = response.json()

# Filter for Crescenta Valley zip codes
crescenta_zip_codes = {
    "91020",  # Montrose
    "91214",  # La Crescenta, Crescenta Highlands (Glendale)
    "91011",  # La Cañada Flintridge
    "91208",  # Sparr Heights, Verdugo Woodlands (Glendale)
    "91046"   # Verdugo City
    # "91202",  # Northern Glendale
    # "91040",  # Sunland
    # "91042",  # Tujunga
}

# Extract boundary polygons for these zip codes
filtered_features = [
    feature for feature in geojson_data["features"]
    if feature["properties"]["ZCTA5CE10"] in crescenta_zip_codes
]

crescenta_boundaries = {"type": "FeatureCollection", "features": filtered_features}

m = folium.Map(
    location=[34.216, -118.227],  # Bottom-left corner of Montrose
    zoom_start=13,
    min_lat=34.20, max_lat=34.27,  # Prevents moving outside latitude
    min_lon=-118.30, max_lon=-118.20,  # Prevents moving outside longitude
    no_wrap=True,
    control_scale=True,
    min_zoom=9,  # Set the minimum zoom level to prevent excessive zooming out
)


# Add boundary polygons with different colors per ZIP code
folium.GeoJson(
    crescenta_boundaries,
    name="Crescenta Valley Boundaries",
    # style_function=zip_color
).add_to(m)

polygons = [shape(feature["geometry"]) for feature in crescenta_boundaries["features"]]
crescenta_multipolygon = MultiPolygon(polygons)

# Step 2: Get bounding box of the entire multipolygon
minx, miny, maxx, maxy = crescenta_multipolygon.bounds

# Step 3: Generate random points within the bounds & test for inclusion
df = pd.DataFrame(columns=['meterValue', 'zipcode', 'serialNumber', 'date', 'timestamp', 'coordinate'])

while len(df) < 250:
    rand_lat = random.uniform(miny, maxy)
    rand_lon = random.uniform(minx, maxx)

    p = Point(rand_lon, rand_lat)

    if crescenta_multipolygon.contains(p):

        # crescenta_boundaries['features'][0]['geometry']['coordinates']
        zipcode = get_zip_from_point(rand_lat, rand_lon, crescenta_boundaries)

        date, timestamp = get_random_date_and_epoch()
        df.loc[len(df)] = {
            'meterValue': get_random_meter_value(),
            'zipcode': zipcode,
            'serialNumber': generate_serial_number(),
            'date': date,
            'timestamp': timestamp,
            'coordinate': (rand_lat, rand_lon)
        }

meters = plugins.MarkerCluster().add_to(m)

# Step 4: Plot on Folium map
for idx, row in df.iterrows():
    lat, lon = row.coordinate
    meterValue = row.meterValue
    serialNumber = row.serialNumber

    label = f'Serial Number: {serialNumber}\n\nMeter Value: {meterValue}'

    folium.Marker(
        location=[lat, lon],
        popup=label
    ).add_to(meters)


##############visualizing and saving
# Save and display map
m.save("crescenta_valley_polygons_with_boundaries.html")
webbrowser.open("../aws/s3-bucket/resources/crescenta_valley_polygons_with_boundaries.html")

# Provide link to open
"Map saved as crescenta_valley_polygons_with_boundaries.html - Open it in a browser to view."