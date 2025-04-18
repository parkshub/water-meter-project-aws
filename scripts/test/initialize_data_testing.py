import boto3
import os
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

# Initialize AWS resources
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

table = dynamodb.Table('WaterMeterData')  # Change this if your table name is different

# Your dataset
values = [595.825, 65.475, 21.86, 313.322, 305.162, 8.898]
zipcodes = ["91020", "91214", "91011", "91208", "91202", "91046"]
serial_numbers = ["9887542664", "3025973645", "8506764888", "9516250994", "5855560432", "2945727439"]
timestamps = [1724490873, 1733504622, 1730295758, 1730129867, 1723244142, 1711808681]
dates = ["2024-08-01", "2024-09-10", "2024-07-15", "2024-06-20", "2024-05-18", "2024-04-05"]

# Insert data into DynamoDB
for i in range(len(values)):
    item = {
        "serialNumber": serial_numbers[i],
        "timestamp": timestamps[i],
        "meterValue": Decimal(str(values[i])),
        "zipCode": zipcodes[i],
        "date": dates[i]
    }
    table.put_item(Item=item)
    print(f"Inserted: {item}")

print("✅ All data inserted successfully!")

# Scan the entire table
response = table.scan()

# Get all items
items = response.get('Items', [])

# Print results
for item in items:
    print(item)

print(f"✅ Retrieved {len(items)} items from DynamoDB!")