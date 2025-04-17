import json
import boto3
import os
import re
from datetime import datetime
from decimal import Decimal
from collections.abc import Mapping, Iterable
from boto3.dynamodb.conditions import Key
import uuid

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

def is_valid_zip(zipcode):
    """Check if ZIP code is exactly 5 digits."""
    return bool(re.fullmatch(r"^\d{5}$", zipcode))

def is_valid_date(date):
    """Check if the date is in YYYY-MM-DD format."""
    return bool(re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", date))

dynamodb = boto3.resource("dynamodb")
MeterTable = dynamodb.Table("WaterMeterTable")
ReferenceTable = dynamodb.Table("MeterReferenceTable")

def lambda_handler(event, context):
    try:
        # Parse JSON body to a dictionary
        body = json.loads(event.get("body", "{}"))

        if not body:
            return {"statusCode": 400, "body": json.dumps({"error": "Empty body"})}

        serial_number = body.get('serialNumber')
        reference_response = ReferenceTable.get_item(Key={'serialNumber': serial_number})
        reference_item = reference_response.get('Item', {})

        if not reference_item:
            return {"statusCode": 400, "body": json.dumps(
                {"error": f"Serial Number, {serial_number}, not found. Please register new meter"})}

        zipcode = reference_item.get('zipcode')
        coordinate = reference_item.get('coordinate')
        meter_value = body.get('meterValue')
        date = body.get('date')

        if not all([serial_number, meter_value, date, zipcode, coordinate]):  # Ensure all fields exist
            return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields"})}

        if not isinstance(meter_value, (int, float, Decimal)):  # Ensure it's a number
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid meterValue. Must be a number."})}

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

        MeterTable.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Item inserted successfully',
                'body': item
            }, cls=DecimalEncoder)
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }