from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda
import os
import uuid
from datetime import datetime
import boto3
import json

_LOG = get_logger('UuidGenerator-handler')


class UuidGenerator(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        # todo implement business logic
        bucket_name = os.getenv('BUCKET_NAME')
        file_content = {
            "ids": [str(uuid.uuid4()) for _ in range(10)]
        }
        # file_name = event["time"]
        file_name = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(file_content), ContentType="application/json")
        _LOG.info(f'event is: {event}')
        return event


HANDLER = UuidGenerator()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
