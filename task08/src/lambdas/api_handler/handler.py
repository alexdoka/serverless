import requests
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger('ApiHandler-handler')

class OpenMeteoAPI(AbstractLambda):
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # def validate_request(self, event) -> dict:
    #     if 'latitude' in event and 'longitude' in event:
    #         return event
    #     else:
    #         raise ValueError("Invalid request: latitude and longitude required")

    def handle_request(self, event, context):
        if 'latitude' not in event and 'longitude' not in event:
            event['longitude'] = "13.41"
            event['latitude'] = "52.52"
        print(event)
        response = requests.get(f"{self.BASE_URL}?latitude={event['latitude']}&longitude={event['longitude']}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


# class ApiHandler(AbstractLambda):
#     def __init__(self):
#         self.weather_api = OpenMeteoAPI()

#     def validate_request(self, event) -> dict:
#         if 'latitude' in event and 'longitude' in event:
#             return event
#         else:
#             raise ValueError("Invalid request: latitude and longitude required")

#     def handle_request(self, event, context):
#         forecast = self.weather_api.get_weather_forecast(event)
#         return {'statusCode': 200, 'body': forecast}

# HANDLER = ApiHandler()

# def lambda_handler(event, context):
#     return HANDLER.lambda_handler(event=event, context=context)
req = OpenMeteoAPI()

def lambda_handler(event, context):
    return req.lambda_handler(event=event, context=context)