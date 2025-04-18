import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from collections.abc import Mapping, Iterable
from decimal import Decimal

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

dynamodb = boto3.resource('dynamodb')
MeterTable = dynamodb.Table('WaterMeterTable')
ReferenceTable = dynamodb.Table('MeterReferenceTable')

def lambda_handler(event, context):
    try:
        s3 = boto3.client('s3')
        bucket_name = 'water-meter-s3-bucket'
        file_name = 'reference.json'
        deserializer = TypeDeserializer()

        try:
            response = s3.get_object(Bucket=bucket_name, Key=file_name)
            content = response['Body'].read().decode('utf-8')
            data = json.loads(content)
        except Exception as e:
            print("Failed to load reference.json:", str(e))
            raise e

        serial_number = None
        new_item = None

        for record in event['Records']:
            try:
                if record['eventName'] == 'INSERT':
                    try:
                        new_item = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['NewImage'].items()}
                        serial_number = new_item['serialNumber']

                        existing = next((item for item in data if item['serialNumber'] == serial_number), None)
                        if not existing:
                            data.append(new_item)
                        else:
                            print(f"serialNumber {serial_number} already exists in reference.json, skipping append")

                    except Exception as e:
                        print("Failed to process INSERT event:", str(e))

                elif record['eventName'] == 'REMOVE':
                    try:
                        old_item = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['OldImage'].items()}
                        serial_number = old_item['serialNumber']
                        data = [item for item in data if item['serialNumber'] != serial_number]
                    except Exception as e:
                        print("Failed to process REMOVE event:", str(e))

                    try:
                        response = MeterTable.query(
                            KeyConditionExpression=boto3.dynamodb.conditions.Key('serialNumber').eq(serial_number)
                        )
                        for item in response.get('Items', []):
                            MeterTable.delete_item(
                                Key={
                                    'serialNumber': item['serialNumber'],
                                    'timestamp': item['timestamp']
                                }
                            )
                    except Exception as e:
                        print("Failed to delete from MeterTable:", str(e))

                elif record['eventName'] == 'MODIFY':
                    try:
                        new_item = {k: deserializer.deserialize(v) for k, v in record['dynamodb']['NewImage'].items()}
                        serial_number = new_item['serialNumber']
                        data = [new_item if item['serialNumber'] == serial_number else item for item in data]
                    except Exception as e:
                        print("Failed to process MODIFY event:", str(e))

                    try:
                        response = MeterTable.query(
                            KeyConditionExpression=boto3.dynamodb.conditions.Key('serialNumber').eq(serial_number)
                        )

                        for item in response.get('Items', []):
                            MeterTable.update_item(
                                Key={
                                    'serialNumber': item['serialNumber'],
                                    'timestamp': item['timestamp']
                                },
                                UpdateExpression="SET zipcode = :zip, coordinate = :coord",
                                ExpressionAttributeValues={
                                    ':zip': new_item['zipcode'],
                                    ':coord': new_item['coordinate']
                                }
                            )
                    except Exception as e:
                        print("Failed to update MeterTable:", str(e))

            except Exception as e:
                print("Error processing record:", str(e))
                continue

        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=json.dumps(data, indent=2, cls=DecimalEncoder)
            )
            print("reference.json updated in S3")
        except Exception as e:
            print("Failed to write reference.json to S3:", str(e))
            raise e

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Reference updated and MeterTable synced'})
        }

    except Exception as e:
        print("Top-level error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
