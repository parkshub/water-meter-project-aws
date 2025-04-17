import json
import urllib.parse
import urllib.request
import boto3
import os

# Get environment variables
cognito_domain = os.environ['COGNITO_DOMAIN']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
redirect_uri = os.environ['REDIRECT_URI']

def lambda_handler(event, context):
    try:
        # Get the authorization code from the request
        body = json.loads(event['body'])
        code = body['code']

        # Prepare the token request
        token_url = f'https://{cognito_domain}/oauth2/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = urllib.parse.urlencode({
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }).encode('ascii')

        # Make the request to Cognito
        req = urllib.request.Request(token_url, data=data, headers=headers, method='POST')
        response = urllib.request.urlopen(req)

        # Parse and return the tokens
        tokens = json.loads(response.read().decode('utf-8'))

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': redirect_uri,
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps(tokens)
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': redirect_uri,
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }