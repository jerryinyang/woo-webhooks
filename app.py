import json, config
import generate_request as f_gen 
from flask import Flask, request, render_template, flash
from classes import API_Account, RequestLog
import handle_variables as var_handler
import time



app = Flask(__name__)
app.secret_key = config.WEBHOOK_TOKEN

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    _, accounts_safe = var_handler.get_accounts()
    logs = var_handler.get_logs()

    if request.method == 'POST':
        password = request.form.get('password', False)

        if password:
            account_name = request.form.get('account_name', False)
            api_key = request.form.get('api_key', False)
            api_secret = request.form.get('api_secret', False)

            if account_name:
                var_handler.add_account(account_name, api_key, api_secret)

            remove_name = request.form.get('remove_name', False)

            if remove_name:
                var_handler.remove_account(remove_name)
        
        # Update the Accounts List
        logs = var_handler.get_logs()
        _, accounts_safe = var_handler.get_accounts()

        return render_template('index.html', data=accounts_safe, logs=logs, reload_page="True")
        
    return render_template('index.html', data=accounts_safe, logs=logs, reload_page="False")


@app.route("/webhook", methods=["POST", "GET", "DELETE"])
def webhook():
    # Receive The Payload (Tradingview Alert)
    payload = request.data
    try:
        payload=json.loads(payload)
    except Exception as e:
        return f_gen.generate_error('Unknown Error : '  + str(e))

    # Create Timestamp and Account Object
    timestamp = f_gen.generate_timestamp()

    # Fetch All API Accounts
    accounts, _ = var_handler.get_accounts()
    list_accounts = []
    all_responses = {}
    
    for _account in accounts:
        _name, _key, _secret = _account
        list_accounts.append(API_Account(_name, _key, _secret))

    for _account in list_accounts: 
        # Generate Request Object From Payload
        account_name = _account.getName()
        try:
            payload_response, list_request = f_gen.payload_to_request(_account, payload, timestamp)
            

        except Exception as e:
            return f_gen.generate_error('Unknown Error : ' + str(e))

        # End The Process with any error in the payload
        if 'ERROR' in payload_response:
            # Create Log Object, and Store it
            var_handler.add_log(RequestLog(timestamp, payload, payload_response))
            return f_gen.generate_error(payload_response)

        # Send Requests for each account and Receive Responses
        responses = []

        for object_request in list_request:
            [request_type , request_url_path, request_header, request_data] = object_request.getData()

            response = f_gen.send_request(request_type, request_url_path, request_header, request_data)

            var_handler.add_log(RequestLog(timestamp, payload, response.json()))
            responses.append(response)
        
        # Add Response to all_responses, Key is the Account Name
        all_responses[account_name] = responses

        # 
        time.sleep(1)

    base_response = {
        'Status' : 'Request Sent Successfully'  
    }

    for account in all_responses.keys():
        responses = all_responses[account]
        response = {}

        for message in responses:
            response.update([
            ('API Response', message.json()),
        ])
        
        var_handler.add_log(RequestLog(timestamp, payload, f'Response [{account}] : ' + str(message)))

        base_response.update([
            (f'Response [{account}]', response)
        ])

    return base_response

