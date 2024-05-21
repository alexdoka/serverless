# from commons.log_helper import get_logger
# from commons.abstract_lambda import AbstractLambda
import json
import os
import boto3
import uuid
from datetime import datetime
import datetime

# _LOG = get_logger('ApiHandler-handler')

user_pool_name = os.getenv('USER_POOL_NAME')
db_table_name = os.getenv('DB_TABLE')
db_reservation_table_name = os.getenv('DB_RESERVATION_TABLE')

HEADERS = {
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': '*',
    'Accept-Version': '*'
}

def convert_dynamodb_item(item):
    converted = {}
    for key, val in item.items():
        if 'N' in val:
            converted[key] = int(val['N'])
        elif 'BOOL' in val:
            converted[key] = val['BOOL']
        elif 'S' in val:
            converted[key] = val['S']
    return converted

class ApiHandler():

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        """
        MAIN HANDLER FUNCTION
        """
        # define user pool id
        def get_user_pool_id(client, usr_pool_name):
            response = client.list_user_pools(MaxResults=60)
            for pool in response['UserPools']:
                if pool['Name'] == usr_pool_name:
                    return pool['Id']
            return None
        
        def get_app_client_id(client, user_pool_id):
            response = client.list_user_pool_clients(UserPoolId=user_pool_id)
            return response['UserPoolClients'][0]['ClientId']

        http_method = event['httpMethod']
        path = event['path']

        ###############################################
        # handle sign up ##############################
        ###############################################
        if http_method == 'POST' and path == '/signup':
            body = json.loads(event['body'])
            email = body['email']
            password = body['password']
            firstName = body['firstName']
            lastName = body['lastName']

            client = boto3.client('cognito-idp')
            user_pool_id = get_user_pool_id(client, user_pool_name)

            # sign up user
            try:
                response = client.admin_create_user(
                    UserPoolId=user_pool_id,
                    Username=email,
                    UserAttributes=[
                        {
                            'Name': 'given_name',
                            'Value': firstName
                        },
                        {
                            'Name': 'family_name',
                            'Value': lastName
                        },
                        {
                            'Name': 'email',
                            'Value': email
                        },
                    ],
                    TemporaryPassword="Testtyu1$%^*",
                    MessageAction='SUPPRESS'
                )
                # Set the user's password
                client.admin_set_user_password(
                    UserPoolId=user_pool_id,
                    Username=email,
                    Password=password,
                    Permanent=True
                )
                return {
                    'statusCode': 200,
                    'body': 'OK',
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }
        ###############################################
        # handle sign in ##############################
        ###############################################
        if http_method == 'POST' and path == '/signin':
            body = json.loads(event['body'])
            email = body['email']
            password = body['password']

            client = boto3.client('cognito-idp')
            user_pool_id = get_user_pool_id(client, user_pool_name)
            app_client_id = get_app_client_id(client, user_pool_id)
            
            print(email, password, user_pool_id, app_client_id)

            try:
                response = client.admin_initiate_auth(
                    UserPoolId=user_pool_id,
                    ClientId=app_client_id,
                    AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                        'PASSWORD': password
                    },
                )
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }

            print(response)
            try:
                response = client.admin_initiate_auth(
                    UserPoolId=user_pool_id,
                    ClientId=app_client_id,
                    AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                        'PASSWORD': password
                    },
                )
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'accessToken': response['AuthenticationResult']['IdToken'],
                    }),
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }
        ###############################################
        # handle GET /tables ##########################
        ###############################################
        if http_method == 'GET' and path == '/tables':
            #  return all record from table Table
            client = boto3.client('dynamodb')
            try:
                client = boto3.client('dynamodb')
                response = client.scan(TableName=db_table_name)
                print(response)
                #  convert items from dynamodb to json
                response['Items'] = [convert_dynamodb_item(item) for item in response['Items']]
                return {
                    'statusCode': 200,
                    'body': json.dumps({ "tables" : response['Items'] }),
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }
            
        ###############################################
        # handle GET /tables/tables_id ################
        ###############################################
        if http_method == 'GET' and path.startswith('/tables/'):
            table_id = path.split('/')[-1]  # Extract tableId from the path

            client = boto3.client('dynamodb')

            try:
                response = client.get_item(
                    TableName=db_table_name,
                    Key={'id': {'N': table_id}}
                )
                print(response)
                # convert dynamodb item to json
                item = convert_dynamodb_item(response['Item'])

                return {
                    'statusCode': 200,
                    'body': json.dumps(item),
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }


        ###############################################
        # handle POST /tables ##########################
        ###############################################
        #  {
        #      "id": // int
        #      "number": // int, number of the table
        #      "places": // int, amount of people to sit at the table
        #      "isVip": // boolean, is the table in the VIP hall
        #      "minOrder": // optional. int, table deposit required to book it
        #  }
        if http_method == 'POST' and path == '/tables':
            body = json.loads(event['body'])
            id = body['id']
            number = body['number']
            places = body['places']
            isVip = body['isVip']
            minOrder = body.get('minOrder', None)

            client = boto3.client('dynamodb')


            try:
                item = {
                    'id': {'N': str(id)},
                    'number': {'N': str(number)},
                    'places': {'N': str(places)},
                    'isVip': {'BOOL': bool(isVip)},
                }

                if minOrder is not None:
                    item['minOrder'] = {'N': str(minOrder)}

                response = client.put_item(
                    TableName=db_table_name,
                    Item=item
                )
                print(response)
                output = {
                    'id': id,
                }
                print(output)

                return {
                    'statusCode': 200,
                    'body': json.dumps(output),
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }


        ###############################################
        # handle POST /reservations ###################
        ###############################################
        if http_method == 'POST' and path == '/reservations':
            body = json.loads(event['body'])
            table_number = body['tableNumber']
            client_name = body['clientName']
            phone_number = body['phoneNumber']
            date = body['date']
            slot_time_start = datetime.datetime.strptime(body['slotTimeStart'], '%H:%M').time()
            slot_time_end = datetime.datetime.strptime(body['slotTimeEnd'], '%H:%M').time()

            client = boto3.client('dynamodb')

            # Get all reservations
            response = client.scan(
                TableName=db_reservation_table_name,
            )
            response_table = client.scan(
                TableName=db_table_name,
            )
            # get all tables number
            tables = [int(item['number']['N']) for item in response_table['Items']]
            print(f"All tables: {tables}")
            
            # Define a function to check if two periods overlap
            def check_overlap(start1, end1, start2, end2):
                return start1 <= end2 and start2 <= end1

            # reservation to non-existed table
            print(f"All data are {table_number} and {tables}")
            if int(table_number) not in tables:
                return {
                    'statusCode': 400,
                    'body': 'Table does not exist'
                }

            for item in response['Items']:
                if item['date']['S'] == date and str(item['tableNumber']['N']) == str(table_number):
                    print(f"Existed item {item}")
                    start_time1 = datetime.datetime.strptime(item['slotTimeStart']['S'], "%H:%M").time()
                    end_time1 = datetime.datetime.strptime(item['slotTimeEnd']['S'], "%H:%M").time()
                    start_time2 = slot_time_start
                    end_time2 = slot_time_end
                    if check_overlap(start_time1, end_time1, start_time2, end_time2):
                        print("Time slot is already reserved")
                        return {
                            'statusCode': 400,
                            'body': 'Time slot is already reserved',
                            'headers': HEADERS
                        }
                    else:
                        print("Time slot is available")

            # # If no overlap, proceed with reservation
            reservation_id = str(uuid.uuid4())

            item = {
                'id': {'S': str(reservation_id)},
                'tableNumber': {'N': str(table_number)},
                'clientName': {'S': client_name},
                'phoneNumber': {'S': phone_number},
                'date': {'S': date},
                'slotTimeStart': {'S': body['slotTimeStart']},
                'slotTimeEnd': {'S': body['slotTimeEnd']},
            }


            try:
                response = client.put_item(
                    TableName=db_reservation_table_name,
                    Item=item
                )
                print(response)
                output = {
                    'reservationId': reservation_id,
                }
                return {
                    'statusCode': 200,
                    'body': json.dumps(output),
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }
        ##############################################
        # handle GET /reservations ###################
        ###############################################
        #     Response:

        #  {
        #      "reservations": [
        #          {
        #              "tableNumber": // int, number of the table
        #              "clientName": //string
        #              "phoneNumber": //string
        #              "date": // string in yyyy-MM-dd format
        #              "slotTimeStart": // string in "HH:MM" format, like "13:00",
        #              "slotTimeEnd": // string in "HH:MM" format, like "15:00"
        #          }
        #      ]
        #  }
        if http_method == 'GET' and path == '/reservations':
            client = boto3.client('dynamodb')
            try:
                response = client.scan(TableName=db_reservation_table_name)
                print(response)
                #  delete from items key 'id'
                for item in response['Items']:
                    del item['id']
                # convert items from dynamodb to json
                response['Items'] = [convert_dynamodb_item(item) for item in response['Items']]
                return {
                    'statusCode': 200,
                    'body': json.dumps({ "reservations" : response['Items'] }),
                    'headers': HEADERS
                }
            except:
                return {
                    'statusCode': 400,
                    'body': 'Bad Request',
                    'headers': HEADERS
                }

        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!',
            'headers': HEADERS
        }

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.handle_request(event=event, context=context)
