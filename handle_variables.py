import pandas as pd
import os.path
import sqlite3
from datetime import datetime
from classes import RequestLog
from config import Config as config
import Google as drive
import asyncio
    
def add_account(name : str, api_key : str, api_secret : str):
    download_database()
    # Add Account Into SQL Database
    SQL_ManageAccount('add', name, api_key, api_secret)

    update_database()
    return f'Account ({name}) added.'

def remove_account(name : str):
    download_database()
    # Remove Account From SQL Database
    SQL_ManageAccount('remove', name, '', '')

    update_database()
    return f'Account ({name}) removed.'

def get_accounts():
    download_database()
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
    download_database()
    new_log = log.getLog()
    timestamp = new_log['timestamp'] 
    command = new_log['command'] 
    response = new_log['response'] 

    if management:
        logs = pd.read_csv('management_logs.csv', sep='|')

        new_log_df = pd.DataFrame({
            'timestamp' : [timestamp], 
            'command' : [command], 
            'response' : [response]
        })

        logs = pd.concat([new_log_df, logs], axis=0, ignore_index=True)
        logs.to_csv('management_logs.csv', index=False, sep='|')

    SQL_ManageLog('add', timestamp, command, response)
    update_database()

def get_logs():
    download_database()
    logs = SQL_ManageLog('get', '', '', '')

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

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "instance\db.sqlite3")

    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        _add = f"INSERT INTO user (api_name, api_key, api_secret) VALUES ('{api_name}', '{api_key}', '{api_secret}')"
        _delete =f"DELETE FROM user WHERE api_name='{api_name}'"
        
        if action == 'add':
            cursor.execute(_add)
            connection.commit()
            return True

        elif action == 'remove':
            cursor.execute(_delete)
            connection.commit()
            return True

        elif action == 'get':
            return pd.read_sql_query("SELECT * FROM user", connection)

def SQL_ManageLog(action, timestamp, command, response):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "instance\db.sqlite3")
    
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        _add = f"INSERT INTO log (timestamp, command, response) VALUES (?,?,?)"

        if action == 'add':
            cursor.execute(_add, (timestamp, command, response))
            connection.commit()
            return True

        if action == 'get':
            return pd.read_sql_query("SELECT * FROM log ORDER BY timestamp DESC", connection)

def download_database():
    service = asyncio.run(drive.Create_Service())
    asyncio.run(drive.Download_File(service, config.DRIVE_FILE_NAME))

def update_database():
    service = asyncio.run(drive.Create_Service())
    asyncio.run(drive.Upload_File(service, config.DRIVE_FOLDER_NAME, config.DRIVE_FILE_NAME, './instance/db.sqlite3', 'sqlite3'))