from Google import *
import asyncio
import pandas as pd
from config import Config as config

service = asyncio.run(Create_Service())

if service is not None:
    # print(asyncio.run(Create_Folder(service, 'Test Folder')))
    # print(Search_File(service, 'Test Folder'))
    # print(asyncio.run(Upload_File(service, 'Test Folder', 'db', './instance/db.sqlite3', 'sqlite3')))
    # print(asyncio.run(Download_File(service, config.DRIVE_FILE_NAME)))
    pass


# df1 = pd.read_csv('accounts.csv', sep=',')
# df2 = pd.read_csv('accounts copy.csv', sep=',')

# df3 = pd.concat([df1, df2]).drop_duplicates()

# print(df3)

# asyncio.run(Download_File(service, config.DRIVE_FILE_NAME_ACCOUNTS))

asyncio.run(Upload_File(service, config.DRIVE_FOLDER_NAME, 'requirements.txt', \
        './requirements.txt', 'text'))