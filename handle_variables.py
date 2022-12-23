import pandas as pd
import os.path
import sqlite3
from datetime import datetime
from classes import RequestLog
from config import Config as config
import Google as drive
import asyncio
import shutil
    
def add_account(name : str, api_key : str, api_secret : str):
    # Add Account Into SQL Database
    if SQL_ManageAccount('add', name, api_key, api_secret):
        asyncio.run(query_database('upload', 'add account', name, api_key, api_secret, None, None, None, "instance\drive_db.sqlite3"))

    return f'Account ({name}) added.'

def remove_account(name : str):
    # Remove Account From SQL Database
    if SQL_ManageAccount('remove', name, '', ''):
        asyncio.run(query_database('upload', 'remove account', name, None, None, None, None, None, "instance\drive_db.sqlite3"))

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
    
    asyncio.run(query_database('download', None, None, None, None, None, None, None, None))
    return list_accounts, list_accounts_safe

def add_log(log : RequestLog, management=False):
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

    if SQL_ManageLog('add', timestamp, command, response):
        asyncio.run(query_database('upload', 'add log', '', '', '', timestamp, command, response, "instance\drive_db.sqlite3"))

def get_logs():
    logs = SQL_ManageLog('get', '', '', '')

    dict_logs = logs.to_dict()

    list_logs = []

    for index in range(logs.shape[0]):
        timestamp = dict_logs['timestamp'][index]
        command = dict_logs['command'][index]
        response = dict_logs['response'][index]

        list_logs.append((datetime.fromtimestamp(int(timestamp/1000)).strftime('%Y-%m-%d %H:%M:%S'),
         command, response))
    
    asyncio.run(query_database('download', None, None, None, None, None, None, None, None))
    return list_logs[:20]

def SQL_ManageAccount(action, api_name, api_key, api_secret, path : str = None):

    _path = path if path is not None else "instance\db.sqlite3"
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, _path)

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

def SQL_ManageLog(action, timestamp, command, response, path : str = None):
    _path = path if path is not None else "instance\db.sqlite3"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, _path)
    
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()

        _add = f"INSERT INTO log (timestamp, command, response) VALUES (?,?,?)"

        if action == 'add':
            cursor.execute(_add, (timestamp, command, response))
            connection.commit()
            return True

        if action == 'get':
            return pd.read_sql_query("SELECT * FROM log ORDER BY timestamp DESC", connection)

async def query_database(query_action : str, task_action : str, name, api_key, api_secret, \
    timestamp, command, response, path):  
  
    service = await asyncio.create_task(drive.Create_Service())
    await asyncio.create_task(drive.Download_File(service, config.DRIVE_FILE_NAME))
    
    # Update Drive Database
    if query_action == 'upload':
        if task_action == 'add account':
            SQL_ManageAccount('add', name, api_key, api_secret, path)
        elif task_action == 'remove account':
            SQL_ManageAccount('remove', name, '', '', path)
        elif task_action == 'add log':
            SQL_ManageLog('add', timestamp, command, response, path)

        asyncio.create_task(drive.Upload_File(service, config.DRIVE_FOLDER_NAME, config.DRIVE_FILE_NAME, \
            F'./instance/{config.DRIVE_FILE_NAME}', 'sqlite3'))

    # Update Local Database
    elif query_action == 'download':
        # Update Local Version using the Drive Version
        shutil.copyfile(F'./instance/{config.DRIVE_FILE_NAME}', './instance/db.sqlite3')