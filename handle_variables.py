import pandas as pd
import sqlite3
from datetime import datetime
from classes import RequestLog
from config import Config as config
    
def add_account(name : str, api_key : str, api_secret : str):
    accounts = pd.read_csv('accounts.csv', sep=',')
    
    if name in accounts['api_name'].unique():
        return f'Account with that name ({name}) already exists.'

    new_account = pd.DataFrame({
        'api_name' : [name], 
        'api_key' : [api_key], 
        'api_secret' : [api_secret]
    })
    accounts = pd.concat([accounts, new_account], axis=0, ignore_index=True)
    accounts.to_csv('accounts.csv', index=False)

    # Add Account Into SQL Database
    SQL_ManageAccount('add', name, api_key, api_secret)
    
    return f'Account ({name}) added.'

def remove_account(name : str):
    accounts = pd.read_csv('accounts.csv', sep=',')

    if name not in accounts['api_name'].unique():
        return f'Account with that name ({name}) does not exist.'

    accounts = accounts[accounts['api_name'] != name]
    accounts.to_csv('accounts.csv', index=False)

    # Add Account Into SQL Database
    SQL_ManageAccount('remove', name, '', '')

    return f'Account ({name}) removed.'

def get_accounts():
    accounts = SQL_ManageAccount('get', '', '', '')
    dict_accounts = accounts.to_dict()

    list_accounts = []
    list_accounts_safe = []

    for index in range(accounts.shape[0]):
        name = dict_accounts['api_name'][index]
        key = dict_accounts['api_key'][index]
        secret = dict_accounts['api_secret'][index]

        list_accounts.append((name, key, secret))
        list_accounts_safe.append((name, key))

        list_accounts.sort()
        list_accounts_safe.sort()
        
    return list_accounts, list_accounts_safe

def add_log(log : RequestLog, management=False):
    log_file = 'logs.csv' if (not management) else 'management_logs.csv'
    logs = pd.read_csv(log_file, sep='|')
    
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
    logs.to_csv(log_file, index=False, sep='|')

    SQL_ManageLog('add', timestamp, command, response)
    
    return 

def get_logs():
    logs = SQL_ManageLog('get', '', '', '')
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

def SQL_ManageAccount(action, api_name, api_key, api_secret):
    connection = sqlite3.connect('instance\db.sqlite3')
    cursor = connection.cursor()

    _add = f"INSERT INTO user (api_name, api_key, api_secret) VALUES ('{api_name}', '{api_key}', '{api_secret}')"
    _delete =f"DELETE FROM user WHERE api_name='{api_name}'"

    sql = _add if action.lower() == 'add' else _delete
    
    if action == 'add':
        cursor.execute(_add)
        connection.commit()
        return True

    if action == 'remove':
        cursor.execute(_delete)
        connection.commit()
        return True

    if action == 'get':
        return pd.read_sql_query("SELECT * FROM user", connection)

def SQL_ManageLog(action, timestamp, command, response):
    connection = sqlite3.connect('instance\db.sqlite3')
    cursor = connection.cursor()

    _add = f"INSERT INTO log (timestamp, command, response) VALUES (?,?,?)"

    if action == 'add':
        cursor.execute(_add, (timestamp, command, response))
        connection.commit()
        return True

    if action == 'get':
        return pd.read_sql_query("SELECT * FROM log ORDER BY timestamp DESC", connection)
