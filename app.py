import json
import os
import generate_request as f_gen 
import handle_variables as var_handler
import asyncio
from classes import API_Account, RequestLog
from config import Config as config
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = config.Webhook_Token
app.app_context().push()

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    api_name = db.Column(db.String(50), unique=True)
    api_key = db.Column(db.String(50))
    api_secret = db.Column(db.String(50))

    def __repr__(self) -> str:
        return f"<User : {self.api_name}>"

class Log(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timestamp = db.Column(db.Integer)
    command = db.Column(db.String(1000))
    response = db.Column(db.String(1000))

    def __repr__(self) -> str:
        return f"<User : {self.response}>"

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    
    _, accounts_safe = var_handler.get_accounts()
    logs = var_handler.get_logs()

    if request.method == 'POST':
        password = request.form.get('password', False)

        if password == app.secret_key:
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
    all_responses = {}
    
    for _user in accounts:
        _name, _key, _secret = _user
        _account = API_Account(_name, _key, _secret)

        # Generate Request Objects From Payload
        try:
            general_list_requests = f_gen.generate_request(_account, payload, timestamp)
        except Exception as e:
            return f_gen.generate_error('Unknown Error : ' + str(e))
        
        for (index, payload_request) in enumerate(general_list_requests):
            payload_response, list_request = payload_request

            # End The Process with any error in the payload
            if 'ERROR' in payload_response:
                # Create Log Object, and Store it
                var_handler.add_log(RequestLog(timestamp, payload, payload_response))
                return f_gen.generate_error(payload_response)
            
            # End The Process when Password is changed
            if 'MANAGEMENT' in payload_response:
                # Create Log Object, and Store it
                var_handler.add_log(RequestLog(timestamp, payload, payload_response), True)
                return f_gen.generate_management(payload_response)

            # Send Requests for each account and Receive Responses
            asyncio.run(f_gen.get_responses(list_request, all_responses, f"Payload {index}: {_name}"))

    base_response = {
        'Status' : 'Request Sent Successfully'  
    }

    for account in all_responses.keys():
        responses = all_responses[account]
        response = {}

        for message in responses:
            response.update([
            ('API Response', message),
        ])
        
        var_handler.add_log(RequestLog(timestamp, payload, f'Response [{account}] : ' + str(message)))

        base_response.update([
            (f'Response [{account}]', response)
        ])

    return base_response

