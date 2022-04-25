import base64
from time import gmtime, strftime
from accounts import accounts
import boto3, uuid

s3_client = boto3.client('s3')
# create a DynamoDB object using the AWS SDK
#dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our tables
#table_logger = dynamodb.Table('AccountsLogger')

# store the current time in a human readable format in a variable
now = strftime("%d %b %Y", gmtime())
logger_timestamp = strftime("%d %b %Y %H:%M:%S", gmtime())

bucket_name = "cloudfrontsearchrelevance"


def lambda_handler(event, context):
    request = event.get("Records")[0].get("cf").get("request")
    headers = request.get("headers")

    authorization_header = headers.get("authorization")



    if not check_authorization_header(authorization_header):
        return {
            'headers': {
                'www-authenticate': [
                    {
                        'key': 'WWW-Authenticate',
                        'value':'Basic'
                    }
                ]
            },
            'status': 401,
            'body': 'Unauthorized'
        }


    return request

def check_authorization_header(authorization_header: list) -> bool:
    if not authorization_header:
        return False
        
    for account in accounts:
        encoded_value = base64.b64encode("{}:{}".format(account.get("email"), account.get("password")).encode('utf-8'))
        check_value = "Basic {}".format(encoded_value.decode(encoding='utf-8'))
        
        if authorization_header[0].get("value") == check_value:
    
            file_name = str(uuid.uuid4()) + ".csv"
            s3_path = "credentials_logs/"+ str(now) + '/' + file_name
            s3 = boto3.resource("s3")
            s3.Bucket(bucket_name).put_object(Key=s3_path, Body=(logger_timestamp + " " + account.get("email") + " " + account.get("password")).encode("utf-8"))
            return True

    return False
    