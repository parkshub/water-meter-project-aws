import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime
import re

def is_valid_zip(zipcode):
    return bool(re.fullmatch(r"^\d{5}$", zipcode))


def is_valid_date(date):
    return bool(re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", date))

dynamodb = boto3.resource('dynamodb')
meter_table = dynamodb.Table('WaterMeterTable')
reference_table = dynamodb.Table('MeterReferenceTable')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', {}))

        if not body:
            return {'statusCode': 400, 'body': json.dumps('Request body is empty')}

        serial_number = body.get('serialNumber', None)
        zipcode = body.get('zipcode', None)
        meter_value = body.get('meterValue', None)
        date = body.get('date', None)
        coordinate = body.get('coordinate', None)

        # Validation Checks
        # if not all([serial_number, meter_value, zip_code, date]): # Ensure all fields exist
        existing = reference_table.get_item(Key={'serialNumber': str(serial_number)})

        if 'Item' in existing:
            return {'statusCode': 409, 'body': json.dumps({'error': f'Serial number {serial_number} already exists'})}

        if not all([serial_number, meter_value, date, zipcode, coordinate]):  # Ensure all fields exist
            return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields"})}

        if not isinstance(meter_value, (int, float, Decimal)):  # Ensure it's a number
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid meterValue. Must be a number."})}

        if not is_valid_zip(zipcode):  # Ensure ZIP code is 5 digits
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid zipCode. Must be 5 digits."})}

        if not is_valid_date(date):  # Ensure date is YYYY-MM-DD
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid date format. Use YYYY-MM-DD."})}

        item = {
            'uuid': str(uuid.uuid4()),
            'serialNumber': str(serial_number),
            'meterValue': Decimal(str(meter_value)),
            'zipcode': str(zipcode),
            'date': str(date),
            'timestamp': int(datetime.utcnow().timestamp()),
            'coordinate': [Decimal(str(coord)) for coord in coordinate]
        }

        reference_item = {
            'serialNumber': item['serialNumber'],
            'zipcode': item['zipcode'],
            'coordinate': item['coordinate']
        }

        reference_table.put_item(Item=reference_item)
        meter_table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Meter registered successfully'})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
