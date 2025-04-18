import json
import boto3
from decimal import Decimal
from datetime import datetime
from collections.abc import Mapping, Iterable

class DecimalEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, Mapping):
            return '{' + ', '.join(f'{self.encode(k)}: {self.encode(v)}' for (k, v) in obj.items()) + '}'
        elif isinstance(obj, Iterable) and not isinstance(obj, str):
            return '[' + ', '.join(map(self.encode, obj)) + ']'
        elif isinstance(obj, Decimal):
            return f'{obj.normalize():f}'
        else:
            return super().encode(obj)

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

bucket_name = 'water-meter-s3-bucket'
df_file = 'df.json'
map_gen_queue_url = "https://sqs.us-west-1.amazonaws.com/<account_id>/map-gen-queue.fifo"
dashboard_gen_queue_url = "https://sqs.us-west-1.amazonaws.com/<account_id>/dashboard-gen-queue.fifo"


def lambda_handler(event, context):
    try:
        for record in event['Records']:
            try:
                body = json.loads(record['body'])
            except Exception as e:
                print("Failed to parse body:", str(e))
                continue

            try:
                event_type = body.get('eventType') or 'unknown'
                new_item = body.get('newItem') if isinstance(body.get('newItem'), dict) else None
                old_item = body.get('oldItem') if isinstance(body.get('oldItem'), dict) else None
                uuid = (
                    new_item.get('uuid')
                    if new_item else
                    old_item.get('uuid')
                    if old_item else
                    'unknown'
                )
            except Exception as e:
                print("Failed during event metadata parsing:", str(e))
                continue

            try:
                response = s3.get_object(Bucket=bucket_name, Key=df_file)
                data = json.loads(response['Body'].read().decode('utf-8'))
            except Exception as e:
                print("Failed to read df.json from S3:", str(e))
                continue

            try:
                if event_type == "INSERT" and new_item:
                    data.append(new_item)
                elif event_type == "MODIFY" and new_item:
                    uid = new_item['uuid']
                    data = [item if item['uuid'] != uid else new_item for item in data]
                elif event_type == "REMOVE" and old_item:
                    uid = old_item['uuid']
                    data = [item for item in data if item['uuid'] != uid]
                else:
                    print("Skipped unrecognized or incomplete event")
            except Exception as e:
                print("Failed to update df in memory:", str(e))
                continue

            try:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=df_file,
                    Body=json.dumps(data, indent=2, cls=DecimalEncoder)
                )
            except Exception as e:
                print("Failed to upload df.json to S3:", str(e))
                continue

            try:
                sqs.send_message(
                    QueueUrl=map_gen_queue_url,
                    MessageBody=json.dumps({
                        "data": data
                    }, cls=DecimalEncoder),
                    MessageGroupId="map-gen"
                )
            except Exception as e:
                print("Failed to send message to map-gen-queue:", str(e))

            try:
                sqs.send_message(
                    QueueUrl=dashboard_gen_queue_url,
                    MessageBody=json.dumps({
                        "data": data
                    }, cls=DecimalEncoder),
                    MessageGroupId="dashboard-gen"
                )
            except Exception as e:
                print("Failed to send message to dashboard-gen-queue:", str(e))

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Processed messages from queue"})
        }

    except Exception as e:
        print("Top-level error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
