from handle_variables import SQL_ManageLog
import pandas as pd
import sqlite3

x = SQL_ManageLog('get', '', '', '')

_delete =f"DELETE FROM user WHERE api_name='testName2'"

    
connection = sqlite3.connect('instance\db.sqlite3')
cursor = connection.cursor()

cursor.execute(_delete)
connection.commit()

print(pd.read_sql_query("SELECT * FROM user", connection))