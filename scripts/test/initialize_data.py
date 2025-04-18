import os
import json
import random
import boto3
import requests
from dotenv import load_dotenv
from decimal import Decimal
import pandas as pd
from shapely.geometry import shape, Point, MultiPolygon
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

boundary_url = "https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/ca_california_zip_codes_geo.min.json"
response = requests.get(boundary_url)
geojson_data = response.json()

crescenta_zip_codes = {
    "91020",  # Montrose
    "91214",  # La Crescenta, Crescenta Highlands (Glendale)
    "91011",  # La Cañada Flintridge
    "91208",  # Sparr Heights, Verdugo Woodlands (Glendale)
    "91046"   # Verdugo City
    # "91202",  # Northern Glendale (omitted)
    # "91040",  # Sunland (omitted)
    # "91042",  # Tujunga (omitted)
}

filtered_features = [
    feature
    for feature in geojson_data['features']
    if feature['properties']['ZCTA5CE10'] in crescenta_zip_codes
]

crescenta_boundaries = {'type': 'FeatureCollection', 'features': filtered_features} # i think this is only needed for folium

with open("../aws/s3-bucket/data/crescenta_boundaries.geojson", "w") as f:
    json.dump(crescenta_boundaries, f)


df = pd.DataFrame(columns=['meterValue', 'serialNumber', 'date', 'timestamp', 'zipcode', 'coordinate'])

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
# probably don't need this part
df.to_json("df_backup.json", orient="records", indent=2)

# todo erase this after testing
df = pd.read_json("df_backup.json", orient="records", convert_dates=False)

load_dotenv()

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

table = dynamodb.Table('WaterMeterTable')

for idx, row in df.iterrows():
    item = {
        'uuid': str(row['uuid']),
        'serialNumber': str(row['serialNumber']),
        'timestamp': int(row['timestamp']),
        'meterValue': Decimal(str(row['meterValue'])),
        'date': str(row['date']),
        'zipcode': str(row['zipcode']),
        # 'coordinate': json.dump(row['coordinate']),
        'coordinate': [Decimal(str(row['coordinate'][0])), Decimal(str(row['coordinate'][1]))]

    }
    table.put_item(Item=item)
