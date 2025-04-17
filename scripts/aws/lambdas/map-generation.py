import json
import boto3
import folium
from folium import plugins

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket_name = 'water-meter-s3-bucket'
        file_name = 'df.json'

        # memo: queue has limit of 256kb
        for record in event['Records']:
            body = json.loads(record.get('body', '{}'))

            # Use event data if present and valid
            if isinstance(body.get('data'), list) and body['data']:
                data = body['data']
                print("Using data from event payload")
            else:
                print("Falling back to df.json from S3")
                response = s3.get_object(Bucket=bucket_name, Key=file_name)
                data = json.loads(response['Body'].read().decode('utf-8'))

        # Deduplicate by latest timestamp for each serialNumber
        latest = {}
        for item in data:
            serial = item['serialNumber']
            ts = int(item['timestamp'])
            if serial not in latest or ts > int(latest[serial]['timestamp']):
                latest[serial] = item
        deduped_data = list(latest.values())
        print("Deduplicated data length:", len(deduped_data))

        # Load boundary GeoJSON
        response = s3.get_object(Bucket=bucket_name, Key='crescenta_boundaries.geojson')
        crescenta_boundaries = json.loads(response['Body'].read().decode('utf-8'))

        # Create Folium map
        m = folium.Map(
            location=[34.216, -118.227],
            zoom_start=13,
            min_lat=34.20, max_lat=34.27,
            min_lon=-118.30, max_lon=-118.20,
            no_wrap=True,
            control_scale=True,
            min_zoom=9,
        )

        folium.GeoJson(crescenta_boundaries, name="Crescenta Valley Boundaries").add_to(m)
        meters = plugins.MarkerCluster().add_to(m)

        for row in deduped_data:
            coord = row.get('coordinate')
            if not isinstance(coord, list) or len(coord) != 2:
                continue
            lat, lon = coord
            label = f"Serial Number: {row['serialNumber']}\n\nMeter Value: {row['meterValue']}"
            folium.Marker(location=[lat, lon], popup=label).add_to(meters)

        # Save and upload updated map
        m.save("/tmp/crescenta_valley_polygons_with_boundaries.html")
        with open('/tmp/crescenta_valley_polygons_with_boundaries.html', 'rb') as f:
            s3.put_object(
                Bucket=bucket_name,
                Key='crescenta_valley_polygons_with_boundaries.html',
                Body=f,
                ContentType='text/html',
                CacheControl='no-cache'
            )
        print("Map updated in S3")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Map generated successfully'})
        }
    except Exception as e:
        print("Error in Lambda:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
