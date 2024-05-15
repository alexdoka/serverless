import requests
import uuid
import boto3
from decimal import Decimal
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger('Processor-handler')

patch_all()

class OpenMeteoAPI(AbstractLambda):
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def handle_request(self, event, context):
        print(event)
        response = requests.get(f"{self.BASE_URL}?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

#  make class to put OpenMeteoAPI response in dynamoDB
class FormateDate(AbstractLambda):
    def mutate(self, mapa):
        mutated = {
            "id": str(uuid.uuid4()),
            "forecast": {
                "elevation": int(mapa["elevation"]),
                "generationtime_ms": Decimal(str(mapa["generationtime_ms"])),
                "hourly": {
                    "temperature_2m": [ Decimal(str(i)) for i in mapa["hourly"]["temperature_2m"] ],
                    "time": [ str(i) for i in mapa["hourly"]["time"] ]
                },
                "hourly_units": {
                    "temperature_2m": str(mapa["hourly_units"]["temperature_2m"]),
                    "time": str(mapa["hourly_units"]["time"])
                },
                "latitude": Decimal(str(mapa["latitude"])),
                "longitude": Decimal(str(mapa["longitude"])),
                "timezone": str(mapa["timezone"]),
                "timezone_abbreviation": str(mapa["timezone_abbreviation"]),
                "utc_offset_seconds": int(mapa["utc_offset_seconds"]),
            }
        }
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('cmtr-03c57de0-Weather-test')
        table.put_item(Item=mutated)

        return mutated


req = OpenMeteoAPI()
mutate = FormateDate()

def lambda_handler(event, context):
    forecast = req.lambda_handler(event=event, context=context)
    return mutate.mutate(forecast)
