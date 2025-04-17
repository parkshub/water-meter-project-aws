import json
import boto3
import datetime

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket_name = 'water-meter-s3-bucket'
        file_name = 'meter_dashboard.html'

        for record in event['Records']:
            body = json.loads(record.get('body', '{}'))
            data = body.get('data', [])

        # Deduplicate by serialNumber with latest timestamp
        latest = {}
        for item in data:
            serial = item['serialNumber']
            ts = int(item['timestamp'])
            if serial not in latest or ts > int(latest[serial]['timestamp']):
                latest[serial] = item
        deduped_data = list(latest.values())

        # Categorize by how old they are
        now = datetime.datetime.utcnow().timestamp()
        buckets = {
            "6+ months old": [],
            "9+ months old": [],
            "12+ months old": []
        }

        for item in deduped_data:
            ts = int(item.get("timestamp", 0))
            months_old = (now - ts) / (60 * 60 * 24 * 30)
            if months_old >= 12:
                buckets["12+ months old"].append(item)
            elif months_old >= 9:
                buckets["9+ months old"].append(item)
            elif months_old >= 6:
                buckets["6+ months old"].append(item)

        # Generate HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Old Meters Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 2rem; background: #f9f9f9; }
                h1 { text-align: center; }
                .section { margin-bottom: 2rem; background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
                .section h2 { margin-top: 0; }
                table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
                th, td { padding: 0.5rem; border: 1px solid #ccc; text-align: left; }
                th { background: #f0f0f0; }
            </style>
        </head>
        <body>
            <h1>Water Meters Needing Update</h1>
        """

        for label, items in buckets.items():
            html += f"""
            <div class="section">
                <h2>{label} ({len(items)})</h2>
                <table>
                    <tr><th>Serial Number</th><th>Meter Value</th><th>Timestamp</th></tr>
            """
            for item in items:
                html += f"<tr><td>{item['serialNumber']}</td><td>{item['meterValue']}</td><td>{item['timestamp']}</td></tr>"
            html += "</table></div>"

        html += "</body></html>"

        # Upload to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=html,
            ContentType='text/html',
            CacheControl='no-cache'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Dashboard uploaded to S3'})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
