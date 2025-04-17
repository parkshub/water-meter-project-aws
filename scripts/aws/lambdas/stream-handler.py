import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from collections.abc import Mapping, Iterable
from decimal import Decimal
from datetime import datetime

class DecimalEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, Mapping):
            return '{' + ', '.join(f'{self.encode(k)}: {self.encode(v)}' for (k, v) in obj.items()) + '}'
        elif isinstance(obj, Iterable) and (not isinstance(obj, str)):
            return '[' + ', '.join(map(self.encode, obj)) + ']'
        elif isinstance(obj, Decimal):
            return f'{obj.normalize():f}'  # Removes trailing 0s, prevents scientific notation
        else:
            return super().encode(obj)

sqs = boto3.client('sqs')
queue_url = "https://sqs.us-west-1.amazonaws.com/<account_id>/df-update-queue.fifo"

def lambda_handler(event, context):
    try:
        deserializer = TypeDeserializer()

        for record in event['Records']:
            event_type = record['eventName']
            old_item = None
            new_item = None

            if 'NewImage' in record['dynamodb']:
                new_item = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['NewImage'].items()}
            if 'OldImage' in record['dynamodb']:
                old_item = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['OldImage'].items()}

            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    "eventType": event_type,
                    "newItem": new_item,
                    "oldItem": old_item
                }, cls=DecimalEncoder),
                MessageGroupId="df-update"
            )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Stream processing successful"})
        }

    except Exception as e:
        print("Error in Lambda:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
