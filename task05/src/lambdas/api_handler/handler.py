from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import uuid
from datetime import datetime
import boto3

_LOG = get_logger('ApiHandler-handler')


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # request (context) example
        # {
        #     "principalId": 1,
        #     "content": {"name": "John", "surname": "Doe"} 
        # }
        # response example (return value)
        # {
        #     "statusCode": 201,
        #     "event":
        #     {
        #         "id":         //uuidv4 hash key
        #         "principalId":     //int
        #         "createdAt":     //date time in ISO 8601 formatted string
        #         "body": { /** 'content' value */ }
        #     }
        # } 
        uuid_key = uuid.uuid4()
        # now = datetime.now()
        # timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        response = {
            "statusCode": 201,
            "event": {
                "id": str(uuid_key),
                "principalId": int(event["principalId"]),
                "createdAt": datetime.now().isoformat(),
                "body": event["content"]
            }
        }
        # write response to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('cmtr-03c57de0-Events-test')
        table.put_item(Item=response["event"])

        return response
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
