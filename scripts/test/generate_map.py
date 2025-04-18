import pandas as pd
import folium
import webbrowser
from folium import plugins
import json
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

with open("../aws/s3-bucket/data/crescenta_boundaries.geojson", "r") as f:
    crescenta_boundaries = json.load(f)

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
).add_to(m)


meters = plugins.MarkerCluster().add_to(m)

# todo here instead of df, it should be db loaded from dynamodb
# todo here instead of df, it should be db loaded from dynamodb
# todo here instead of df, it should be db loaded from dynamodb
df_map = pd.read_json("../aws/s3-bucket/data/df.json", orient="records", convert_dates=False)
df_map[df_map['serialNumber']==1824773589]



dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

table = dynamodb.Table('WaterMeterData')

response = table.scan()
items = response['Items']

df_map = pd.DataFrame(items)
df_map = df_map.sort_values('timestamp').drop_duplicates('serialNumber', keep='last')



# Step 4: Plot on Folium map
for idx, row in df_map.iterrows():
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

# df.iloc[0, :]
# test[test['serialNumber']=='3360821092']