from commons.abstract_lambda import AbstractLambda
import json

class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # todo implement business logic
        # path = event['requestContext']['http']['path']

        # if path == '/hello':
        #     # Return response for root path
        #     return {
        #         'statusCode': 200,
        #         'headers': {'Content-Type': 'application/json'},
        #         'body': json.dumps({"statusCode": 200, "message": "Hello from Lambda"})
        #     }

        #     # Default response for other paths
        # return {
        #     'statusCode': 404,
        #     'headers': {'Content-Type': 'application/json'},
        #     'body': json.dumps({'message': 'Not Found'})
        # }
        return {
            "statusCode": 200,
            "message": "Hello from Lambda"
        }
    

HANDLER = HelloWorld()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
