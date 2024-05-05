from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import uuid
from datetime import datetime
import boto3

_LOG = get_logger('AuditProducer-handler')


class AuditProducer(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def handle_request(self, event, context):
        """
        Explain incoming event here
        """

        key = event['Records'][0]['dynamodb']['Keys']['key']['S']
        newValue = event['Records'][0]['dynamodb']['NewImage']['value']['N']

        output = {
            "id": str(uuid.uuid4()),
            "itemKey": key,
            "modificationTime": datetime.now().isoformat()
        }
        if 'OldImage' in event['Records'][0]['dynamodb']:
            oldValue = event['Records'][0]['dynamodb']['OldImage']['value']['N']
            output.update({
                "updatedAttribute": "value",
                "oldValue": int(oldValue),
                "newValue": int(newValue)
            })
        else:
            output.update({
                "newValue": {
                    "key": key,
                    "value": int(newValue)
                }
            })
        print(output)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('cmtr-03c57de0-Audit-test')
        table.put_item(Item=output)
        return output


HANDLER = AuditProducer()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
