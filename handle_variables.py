import pandas as pd
from datetime import datetime
from classes import RequestLog

def add_account(name : str, api_key : str, api_secret : str):
    accounts = pd.read_csv('accounts.csv', sep=',')
    
    if name in accounts['name'].unique():
        return f'Account with that name ({name}) already exists.'

    new_account = pd.DataFrame({
        'name' : [name], 
        'api_key' : [api_key], 
        'api_secret' : [api_secret]
    })
    accounts = pd.concat([accounts, new_account], axis=0, ignore_index=True)
    accounts.to_csv('accounts.csv', index=False)
    
    return f'Account ({name}) added.'

def remove_account(name : str):
    accounts = pd.read_csv('accounts.csv', sep=',')

    if name not in accounts['name'].unique():
        return f'Account with that name ({name}) does not exist.'

    accounts = accounts[accounts['name'] != name]
    accounts.to_csv('accounts.csv', index=False)
    return f'Account ({name}) removed.'

def get_accounts():
    accounts = pd.read_csv('accounts.csv', sep=',')
    dict_accounts = accounts.to_dict()

    list_accounts = []
    list_accounts_safe = []
    

    for index in range(accounts.shape[0]):
        name = dict_accounts['name'][index]
        key = dict_accounts['api_key'][index]
        secret = dict_accounts['api_secret'][index]

        list_accounts.append((name, key, secret))
        list_accounts_safe.append((name, key))

        list_accounts.sort()
        list_accounts_safe.sort()
    return list_accounts, list_accounts_safe

def add_log(log : RequestLog):
    logs = pd.read_csv('logs.csv', sep='|')
    
    new_log = log.getLog()
    timestamp = new_log['timestamp'] 
    command = new_log['command'] 
    response = new_log['response'] 

    new_log = pd.DataFrame({
        'timestamp' : [timestamp], 
        'command' : [command], 
        'response' : [response]
    })

    logs = pd.concat([new_log, logs], axis=0, ignore_index=True)
    logs.to_csv('logs.csv', index=False, sep='|')
    
    return 

def get_logs():
    logs = pd.read_csv('logs.csv', sep='|')
    # logs['timestamp'] = pd.to_datetime(logs['timestamp'], unit='s') # Convert Integer timestamp to datetime

    dict_logs = logs.to_dict()

    list_logs = []

    for index in range(logs.shape[0]):
        timestamp = dict_logs['timestamp'][index]
        command = dict_logs['command'][index]
        response = dict_logs['response'][index]

        list_logs.append((datetime.fromtimestamp(int(timestamp/1000)).strftime('%Y-%m-%d %H:%M:%S'),
         command, response))
    return list_logs[:20]

def see_log():
    logs = pd.read_csv('logs.csv', sep='|')
    
    logs['timestamp'] = pd.to_datetime(logs['timestamp'])
    print(logs)
    return

