import hmac
import hashlib
import datetime
import json
import requests
import math

from classes import API_Account, PayloadRequest
from syntax import *

def get_account_info(_account : API_Account, value : str):
    account_key = _account.getKey()
    account_secret = _account.getSecret()

    timestamp = generate_timestamp()
    _message = f'|{timestamp}'
    signature = generate_signature(_message, account_secret)
    data = {}

    headers = {
    'x-api-timestamp': f'{timestamp}',
    'x-api-key': f'{account_key}',
    'x-api-signature': f'{signature}', 
    'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control':'no-cache' 
    } 
    
    if value == 'USDT Holding':
        response = requests.get('https://api.woo.org/v1/client/holding', headers=headers, data=data)
        return response.json()['holding']['USDT']
    
    if value == 'leverage':
        response = requests.get('https://api.woo.org/v1/client/info', headers=headers, data=data)
        return response.json()['application']['leverage']

def get_latest_price(_account : API_Account, symbol : str):
    account_key = _account.getKey()
    account_secret = _account.getSecret()

    timestamp = generate_timestamp()
    _message = f'limit=1&symbol={symbol}&type=1m|{timestamp}'
    signature = generate_signature(_message, account_secret)

    headers = {
        'x-api-timestamp': f'{timestamp}',
        'x-api-key': f'{account_key}',
        'x-api-signature': f'{signature}',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control':'no-cache'
    }
    response = requests.get(f'https://api.woo.org/v1/kline?limit=1&symbol={symbol}&type=1m', headers=headers )

    try:
        return response.json()['rows'][0]['close']
    except Exception as e:
        return e

def get_min_tick(symbol : str):
    response = requests.get(f'https://api.woo.org/v1/public/info/{symbol}')
    return int(abs(math.log10(response.json()['info']['base_tick'])))

def set_leverage(_account : API_Account, leverage): 
    account_key = _account.getKey()
    account_secret = _account.getSecret()

    timestamp = generate_timestamp()
    _message = 'leverage={leverage}|{timestamp}'.format(leverage=leverage, timestamp=timestamp)
    signature = generate_signature(_message, account_secret)
    data = { 
    'leverage': f'{leverage}'
    }

    headers = {
    'x-api-timestamp': f'{timestamp}',
    'x-api-key': f'{account_key}',
    'x-api-signature': f'{signature}', 
    'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control':'no-cache' 
    } 

    response = requests.post('https://api.woo.org/v1/client/leverage', headers=headers, data=data)
    return response.json()['success']

def generate_request(_account : API_Account , _payload : str, _timestamp : str):
    list_payload = payload_handler(_payload)

    list_request = []
    for payload in list_payload:
        list_request.append(payload_to_request(_account, payload, _timestamp))

    return list_request

def send_request(_type, url, headers, data):
    if (_type == 'cancel-all') or (_type == 'cancel-limit') or (_type == 'cancel-stop'):
        return requests.delete(url, headers=headers, data=data)
    
    return requests.post(url, headers=headers, data=data)

def generate_error(message):
    return {
        "code" : "Failed",
        "message" : message
    }

def generate_timestamp():
    timenow = datetime.datetime.now()
    return str(int(1000 * timenow.timestamp()))

def generate_signature(_message : str, api_secret : str):
    return hmac.new(
        api_secret.encode('utf-8'),
        msg=_message.encode('utf-8'),
        digestmod=hashlib.sha256).hexdigest()

def payload_handler(_payload):
    """Converts Payload String from Tradingview Alerts into Payload Dictionary.

    Args:
        payload (string) : Alert Message from Tradingview.

    Returns:
        A List containing a Tuple(s) of 
            - dictionary/dictionaries, with alert/payload elements.
            - A response message for any errors encountered.

    Raises:
        ERROR (Cannot Read Alert Message): If the parsed payload string is not readable.
    """

    list_payload = []

    # Multiple Requests in One Payload
    if ';' in _payload:
        all_payloads = _payload.split(';')

        for payload in all_payloads:
            try:
                # Prepare Payload
                payload = payload.strip().replace(' ', '').split(',')
            
                # Seperate Payload into Dictionary
                payload_dict = {}
                for item in payload:
                    (key, value) = item.lower().split('=')
                    payload_dict[key] = value.replace('\'', '').replace('\"', '').upper()
                
                response_message = 'Success'

            except:
                # ERROR: Unknown Error
                payload_dict = {}
                response_message = 'ERROR (Cannot Read Alert Message or Messages) : \
                    Make sure your alert messages are written and punctuated correctly, and Separated with a ';''
            
            list_payload.append((payload_dict, response_message))
        
        return list_payload

    # Single Request in a Payload
    try:
        # Prepare Payload
        payload = _payload.strip().replace(' ', '').split(',')
    
        # Seperate Payload into Dictionary
        payload_dict = {}
        for item in payload:
            (key, value) = item.lower().split('=')
            payload_dict[key] = value.replace('\'', '').replace('\"', '').upper()
        
        response_message = 'Success'

    except:
        # ERROR: Unknown Error
        payload_dict = {}
        response_message = 'ERROR (Cannot Read Alert Message) : \
            Make sure your alert message is written and punctuated correctly.'
    
    list_payload.append((payload_dict, response_message))


    return list_payload

def payload_to_request(_account : API_Account , _payload : str, _timestamp : str):
    """
        Returns:
            Response_Message: String Describing the error that may have occured during the function call.
            List of Request Object: Returns a list of request objects; can return more than one request objects
    """
    response_message = ''
    data = ''
    url_path = ''
    header = ''

    payload_dict, response_message = _payload
    if 'ERROR' in response_message:
        return (response_message, None)

    #region ----- Authenticate Payload
    if 'token' not in payload_dict.keys():
        response_message = 'ERROR (Payload Not Authenticated) : \'token\' parameter is required to authenticate payload.'
        return (response_message, None)
    
    _token  = payload_dict['token'].lower()
    
    # ERROR: Check if token matches the stored token
    if _token != config.WEBHOOK_TOKEN:
        response_message = 'ERROR (Wrong Authentication Token) : Wrong Authentication Token.'
        return response_message, None
    #endregion

    #region ----- Confirm Payload Type

    # ERROR: if 'type' key is not in payload
    if 'type' not in payload_dict.keys():
        response_message = 'ERROR (Missing Required Parameter) : \'type\' parameter is not defined.'
        return (response_message, None)
    
    _type = payload_dict['type'].lower().replace(' ', '-').replace('_', '-')
    
    # ERROR: Check if valid argument was passed for 'type' parameter
    if _type not in CONST_TYPES:
        response_message = 'ERROR (Invalid Arguments Passed) : \'{type}\' argument passed for \'type\' parameter is not valid/recognized.'\
            .format(type=_type)
        return (response_message, None)
    #endregion

    #region ----- Alternative Algorithm For Multiple Cancels
    if _type == 'cancel-all':
        list_type = ['cancel-limit', 'cancel-stop']
        
        list_request = []
        for current_type in list_type:
            _required_params = {}

            # Load Required Parameters from Payload Dictionary
            for _param in DICT_PARAMS[current_type]:
                # ERROR: Check for missing required parameter;
                if _param not in payload_dict.keys():
                    response_message = 'ERROR (Missing Required Parameter) : \'{type}\' order requires a \'{param}\' argument.'\
                        .format(type=current_type, param=_param)
                    return (response_message, None)

                # CONTINUE LOGIC : Order type is defined, and all the required arguments have been passed. Collect required parameters
                else:
                    # Check if valid argument has been passed for 'side' parameter
                    if (_param == 'side') and (payload_dict[_param] not in CONST_SIDE):
                        response_message = 'ERROR (Invalid Arguments Passed) : \'{side}\' argument passed for \'side\' parameter is not valid/recognized.'\
                            .format(side=payload_dict[_param])
                        return (response_message, None)
                    
                    _required_params[_param] = payload_dict[_param]

            # Generate Request Body and Normalised Body
            url_path = DICT_URL[current_type]
            header = DICT_HEADER[current_type].copy()
            data = DICT_DATA[current_type].copy()

            _normal_body = DICT_NORMAL[current_type]

            if current_type == 'cancel-limit' :
                _symbol = _required_params['symbol']

                data.update(
                    symbol = _symbol
                    )

                _normal_body = _normal_body.format(symbol=_symbol)
                _normal_body = '{message}{timestamp}'.format(message=_normal_body, timestamp=_timestamp)
            
            elif current_type == 'cancel-stop' :
                _symbol = _required_params['symbol']
                _side = _required_params['side']

                url_path = url_path.format(symbol=_symbol)
                data.update(
                    side = _side
                    )
                data = json.dumps(data)

                _normal_body = _normal_body.format(data=data, symbol=_symbol)
                _normal_body = '{timestamp}{message}'.format(message=_normal_body, timestamp=_timestamp)
            
            # Generate Signature From Normalized Body
            account_key = _account.getKey()
            account_secret = _account.getSecret()
            signature = generate_signature(_normal_body, account_secret)

            # Generate Header
            header.update([
                ('x-api-key', f"{account_key}"),
                ('x-api-signature', f"{signature}"),
                ("x-api-timestamp", f"{_timestamp}") 
                ])

            # Create a Request Object with the results
            request = PayloadRequest(current_type, url_path, header, data, _timestamp)

            list_request.append(request)
        
        return (response_message, list_request)
    #endregion
    
    #region ----- Confirm Required Parameters
    _required_params = {}
    # Load Required Parameters from Payload Dictionary
    for _param in DICT_PARAMS[_type]:
        # ERROR: Check for missing required parameter;
        if _param not in payload_dict.keys():
            response_message = 'ERROR (Missing Required Parameter) : \'{type}\' order requires a \'{param}\' argument.'\
                .format(type=_type, param=_param)
            return (response_message, None)

        # CONTINUE LOGIC : Order type is defined, and all the required arguments have been passed. Collect required parameters
        else:
            # Check if valid argument has been passed for 'side' parameter
            if (_param == 'side') and (payload_dict[_param] not in CONST_SIDE):
                response_message = 'ERROR (Invalid Arguments Passed) : \'{side}\' argument passed for \'side\' parameter is not valid/recognized.'\
                    .format(side=payload_dict[_param])
                return (response_message, None)
            
            # Check if valid argument has been passed for 'leverage' parameter
            if (_param == 'leverage') and (payload_dict[_param] not in CONST_LEVERAGE):
                response_message = 'ERROR (Invalid Arguments Passed) : \'{leverage}\' argument passed for \'leverage\' parameter is not valid/recognized.'\
                    .format(leverage=payload_dict[_param])
                return (response_message, None)
            
            _required_params[_param] = payload_dict[_param]
    #endregion

    #region ----- Generate Request Body and Normalised Body
    url_path = DICT_URL[_type]
    header = DICT_HEADER[_type].copy()
    data = DICT_DATA[_type].copy()

    _normal_body = DICT_NORMAL[_type]

    if _type == 'market' :
        _symbol = _required_params['symbol']
        _side = _required_params['side']
        _order_quantity = _required_params['quantity']
        _leverage = _required_params['leverage']
        _percentage = _required_params['is_percentage']

        # First : Update the Leverage Settings
        set_leverage(_account, _leverage)

        # Next : Calculate Quantity Amount
        if _percentage == 'TRUE':
            current_holding = get_account_info(_account, 'USDT Holding')
            current_price = get_latest_price(_account, _symbol)

            _order_quantity = round((current_holding * (float(_order_quantity) / 100)) / current_price, get_min_tick(_symbol))

        data.update(
            symbol = _symbol,
            side = _side,
            order_quantity = _order_quantity
            )

        print('Last', _order_quantity)

        _normal_body = _normal_body.format(symbol=_symbol, side=_side, order_quantity=_order_quantity)
        _normal_body = '{message}{timestamp}'.format(message=_normal_body, timestamp=_timestamp)

    elif _type == 'limit' :
        _symbol = _required_params['symbol']
        _side = _required_params['side']
        _order_price = _required_params['price']
        _order_quantity = _required_params['quantity']
        _leverage = _required_params['leverage']
        _percentage = _required_params['is_percentage']

        # First : Update the Leverage Settings
        set_leverage(_account, _leverage)

        # Next : Calculate Quantity Amount
        if _percentage == 'TRUE':
            current_holding = get_account_info(_account, 'USDT Holding')
            current_price = get_latest_price(_account, _symbol)

            _order_quantity = round((current_holding * (float(_order_quantity) / 100)) / current_price, get_min_tick(_symbol))

        data.update(
            symbol = _symbol,
            side = _side,
            order_price = _order_price,
            order_quantity = _order_quantity
            )

        _normal_body = _normal_body.format(symbol=_symbol, side=_side, order_price=_order_price, order_quantity=_order_quantity)
        _normal_body = '{message}{timestamp}'.format(message=_normal_body, timestamp=_timestamp)

    elif _type == 'close' :
        _symbol = _required_params['symbol']
        _side = 'BUY' if (_required_params['side'] == 'SELL') else 'SELL'
        _order_quantity = _required_params['quantity']

        data.update(
            symbol = _symbol,
            side = _side,
            order_quantity = _order_quantity
            )

        _normal_body = _normal_body.format(symbol=_symbol, side=_side, order_quantity=_order_quantity)
        _normal_body = '{message}{timestamp}'.format(message=_normal_body, timestamp=_timestamp)

    elif _type == 'cancel-limit' :
        _symbol = _required_params['symbol']

        data.update(
            symbol = _symbol
            )

        _normal_body = _normal_body.format(symbol=_symbol)
        _normal_body = '{message}{timestamp}'.format(message=_normal_body, timestamp=_timestamp)
    
    elif _type == 'cancel-stop' :
        _symbol = _required_params['symbol']
        _side = _required_params['side']

        url_path = url_path.format(symbol=_symbol)
        data.update(
            side = _side
            )
        data = json.dumps(data)

        _normal_body = _normal_body.format(data=data, symbol=_symbol)
        _normal_body = '{timestamp}{message}'.format(message=_normal_body, timestamp=_timestamp)

    elif _type == 'stop' :
        _symbol = _required_params['symbol']
        _side = _required_params['side']
        _price = _required_params['price']
        _quantity = _required_params['quantity']
        _leverage = _required_params['leverage']
        _percentage = _required_params['is_percentage']

        # First : Update the Leverage Settings
        set_leverage(_account, _leverage)

        # Next : Calculate Quantity Amount
        if _percentage == 'TRUE':
            current_holding = get_account_info(_account, 'USDT Holding')
            current_price = get_latest_price(_account, _symbol)

            _order_quantity = round((current_holding * (float(_order_quantity) / 100)) / current_price, get_min_tick(_symbol))

        data.update(
            symbol = _symbol,
            side = _side,
            triggerPrice = _price,
            quantity = _quantity
            )
        data = json.dumps(data)

        _normal_body = _normal_body.format(data=data)
        _normal_body = '{timestamp}{message}'.format(message=_normal_body, timestamp=_timestamp)

    elif _type == 'tp-sl' :


        _side = 'BUY' if (_required_params['side'] == 'sell') else 'SELL'

        _symbol = _required_params['symbol']
        _tp = _required_params['tp']
        _sl = _required_params['sl']
        _reduce = _required_params['reduce_only'].lower()
        
        if float(_tp) == 0:
            data = DICT_DATA['sl']
            data["symbol"] = _symbol
            data["childOrders"][0]['triggerPrice'] = _sl
            data["childOrders"][0]['side'] = _side
            data["childOrders"][0]['reduceOnly'] = _reduce

        elif float(_sl) == 0:
            data = DICT_DATA['tp']
            data["symbol"] = _symbol
            data["childOrders"][0]['triggerPrice'] = _tp
            data["childOrders"][0]['side'] = _side
            data["childOrders"][0]['reduceOnly'] = _reduce

        else:
            data["symbol"] = _symbol
            data["childOrders"][0]['triggerPrice'] = _tp
            data["childOrders"][1]['triggerPrice'] = _sl
            data["childOrders"][0]['side'] = _side
            data["childOrders"][1]['side'] = _side
            data["childOrders"][0]['reduceOnly'] = _reduce
            data["childOrders"][1]['reduceOnly'] = _reduce
        data = json.dumps(data)

        _normal_body = _normal_body.format(data=data)
        _normal_body = '{timestamp}{message}'.format(message=_normal_body, timestamp=_timestamp)
    
    #endregion

    # Generate Signature From Normalized Body
    account_key = _account.getKey()
    account_secret = _account.getSecret()
    signature = generate_signature(_normal_body, account_secret)

    # Generate Header
    header.update([
        ('x-api-key', f"{account_key}"),
        ('x-api-signature', f"{signature}"),
        ("x-api-timestamp", f"{_timestamp}") 
        ])

    # Create a Request Object with the results
    response_message = 'SUCCESS : Request Generated Successfully.'
    request = PayloadRequest(_type, url_path, header, data, _timestamp)
    return (response_message, [request])




