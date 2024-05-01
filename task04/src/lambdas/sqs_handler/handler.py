from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger('SqsHandler-handler')


class SqsHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        Explain incoming event here
        """
        records = event.get('Records', [])
        for record in records:
            message = record.get('body')
            _LOG.info(message)
        return 200
    

HANDLER = SqsHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
