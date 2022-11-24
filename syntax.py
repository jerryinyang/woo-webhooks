import config

CONST_TYPES = ['market', 'limit', 'close', 'cancel-limit', 'cancel-stop', 'cancel-all', 'stop', 'tp-sl']
CONST_SIDE = ['BUY', 'SELL']

# URL 
URL_ORDER_MARKET = config.BASE_URL + '/v1/order'
URL_ORDER_LIMIT = config.BASE_URL + '/v1/order'
URL_POSITION_CLOSE = config.BASE_URL + '/v1/order'
URL_ORDER_CANCEL_LIMIT = config.BASE_URL + '/v1/orders' # Limit Orders 

URL_ORDER_CANCEL_STOP = config.BASE_URL + '/v3/merge/orders/pending/{symbol}'
URL_ORDER_STOP = config.BASE_URL + '/v3/algo/order'
URL_ORDER_TP_SL = config.BASE_URL + '/v3/algo/order'

DICT_URL = {
    'market' : URL_ORDER_MARKET, 
    'limit' : URL_ORDER_LIMIT, 
    'close' : URL_POSITION_CLOSE, 
    'cancel-limit' : URL_ORDER_CANCEL_LIMIT,
    'cancel-stop' : URL_ORDER_CANCEL_STOP, 

    'stop' : URL_ORDER_STOP,
    'tp-sl' : URL_ORDER_TP_SL
    }


# REQUIRED PARAMETERS
PARAMS_ORDER_MARKET = ['symbol', 'side', 'quantity']
PARAMS_ORDER_LIMIT = ['symbol', 'side', 'price', 'quantity']
PARAMS_POSITION_CLOSE = ['symbol', 'side', 'quantity']
PARAMS_ORDER_CANCEL_LIMIT = ['symbol']

PARAMS_ORDER_CANCEL_STOP = ['symbol', 'side']
PARAMS_ORDER_STOP = ['symbol', 'side', 'price', 'quantity']
PARAMS_ORDER_TP_SL = ['symbol', 'tp', 'sl', 'side', 'reduce_only']

DICT_PARAMS = {
    'market' : PARAMS_ORDER_MARKET, 
    'limit' : PARAMS_ORDER_LIMIT, 
    'close' : PARAMS_POSITION_CLOSE, 
    'cancel-limit' : PARAMS_ORDER_CANCEL_LIMIT, 
    'cancel-stop': PARAMS_ORDER_CANCEL_STOP, 

    'stop' : PARAMS_ORDER_STOP,
    'tp-sl' : PARAMS_ORDER_TP_SL
    }


# NORMALIZED MESSAGE
NORMAL_ORDER_MARKET = "order_quantity={order_quantity}&order_type=MARKET&side={side}&symbol={symbol}|"
NORMAL_ORDER_LIMIT = "order_price={order_price}&order_quantity={order_quantity}&order_type=LIMIT&side={side}&symbol={symbol}|"
NORMAL_POSITION_CLOSE = "order_quantity={order_quantity}&order_type=MARKET&side={side}&symbol={symbol}|"
NORMAL_ORDER_CANCEL_LIMIT = "symbol={symbol}|"

NORMAL_ORDER_CANCEL_STOP = "DELETE/v3/merge/orders/pending/{symbol}{data}"
NORMAL_ORDER_STOP = "POST/v3/algo/order{data}"
NORMAL_ORDER_TP_SL = "POST/v3/algo/order{data}"

DICT_NORMAL = {
    'market' : NORMAL_ORDER_MARKET, 
    'limit' : NORMAL_ORDER_LIMIT, 
    'close' : NORMAL_POSITION_CLOSE, 
    'cancel-limit' : NORMAL_ORDER_CANCEL_LIMIT,
    
    'cancel-stop' : NORMAL_ORDER_CANCEL_STOP, 
    'stop' : NORMAL_ORDER_STOP,
    'tp-sl' : NORMAL_ORDER_TP_SL
    }


# DATA BODY
DATA_ORDER_MARKET = { 
    'order_quantity': 0, 
    'order_type': 'MARKET',
    'side': '{side}',
    'symbol': '{symbol}'
    }

DATA_ORDER_LIMIT = { 
    'order_price' : 0,
    'order_quantity': 0, 
    'order_type': 'LIMIT',
    'side':'{side}',
    'symbol': '{symbol}'
    } 

DATA_POSITION_CLOSE = { 
    'order_quantity': 0, 
    'order_type': 'MARKET',
    'side': '{side}',
    'symbol': '{symbol}'
    }

DATA_ORDER_CANCEL_LIMIT = { 
    'symbol': '{symbol}'
    }

DATA_ORDER_CANCEL_STOP = {
    "side":"{side}"
}

DATA_ORDER_STOP = {
    "symbol":"{symbol}",
    "side":"{side}",
    "orderCombinationType":"STOP_MARKET",
    "algoType":"STOP",
    "triggerPrice":"{price}",
    "type":"MARKET",
    "quantity":"{quantity}"
    }

DATA_TP_SL = {
    "symbol": "{symbol}",
    "reduceOnly": 'false',
    "algoType": "POSITIONAL_TP_SL",
    "childOrders": [
        {
            "algoType": "TAKE_PROFIT",
            "type": "CLOSE_POSITION",
            "side": "{side}",
            "reduceOnly": "{reduce_only}",
            "triggerPrice": "{tp_price}"
        },
        {
            "algoType": "STOP_LOSS",
            "type": "CLOSE_POSITION",
            "side": "{side}",
            "reduceOnly": "{reduce_only}",
            "triggerPrice": "{sl_price}"
        }
    ]
}

DATA_TP = {
    "symbol": "{symbol}",
    "reduceOnly": 'false',
    "algoType": "POSITIONAL_TP_SL",
    "childOrders": [
        {
            "algoType": "TAKE_PROFIT",
            "type": "CLOSE_POSITION",
            "side": "{side}",
            "reduceOnly": "{reduce_only}",
            "triggerPrice": "{tp_price}"
        }
    ]
}

DATA_SL = {
    "symbol": "{symbol}",
    "reduceOnly": 'false',
    "algoType": "POSITIONAL_TP_SL",
    "childOrders": [
        {
            "algoType": "STOP_LOSS",
            "type": "CLOSE_POSITION",
            "side": "{side}",
            "reduceOnly": '{reduce_only}',
            "triggerPrice": "{sl_price}"
        }
    ]
}

DICT_DATA = {
    'market' : DATA_ORDER_MARKET, 
    'limit' : DATA_ORDER_LIMIT, 
    'close' : DATA_POSITION_CLOSE, 
    'cancel-limit' : DATA_ORDER_CANCEL_LIMIT,
    'cancel-stop' : DATA_ORDER_CANCEL_STOP, 
    
    'stop' : DATA_ORDER_STOP,
    'tp' : DATA_TP,
    'sl' : DATA_SL,
    'tp-sl' : DATA_TP_SL
    }


# HEADERS 
HEADER_ORDER_MARKET = HEADER_ORDER_LIMIT = HEADER_POSITION_CLOSE = HEADER_ORDER_CANCEL_LIMIT = {
    'x-api-timestamp': '{timestamp}',
    'x-api-key': '{api_key}',
    'x-api-signature': '{signature}', 
    'Content-Type': 'application/x-www-form-urlencoded', 'Cache-Control':'no-cache' 
    } 

HEADER_ORDER_CANCEL_STOP = HEADER_ORDER_STOP = HEADER_POSITION_TP_SL = {
    'x-api-timestamp': '{timestamp}',
    'x-api-key': '{api_key}',
    'x-api-signature': '{signature}', 
    'Content-Type': 'application/json', 
    'Cache-Control':'no-cache' 
    }

DICT_HEADER = {
    'market' : HEADER_ORDER_MARKET, 
    'limit' : HEADER_ORDER_LIMIT, 
    'close' : HEADER_POSITION_CLOSE, 
    'cancel-limit' : HEADER_ORDER_CANCEL_LIMIT,
    'cancel-stop' : HEADER_ORDER_CANCEL_STOP, 
    
    'stop' : HEADER_ORDER_STOP,
    'tp-sl' : HEADER_POSITION_TP_SL
    }