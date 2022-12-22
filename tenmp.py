from Google import *
import asyncio

service = asyncio.run(Create_Service())

if service is not None:
    # print(asyncio.run(Create_Folder(service, 'Test Folder')))
    # print(Search_File(service, 'Test Folder'))
    print(asyncio.run(Upload_File(service, 'Test Folder', 'db', './instance/db.sqlite3', 'sqlite3')))
    # print(asyncio.run(Download_File(service, 'db.sqlite3')))


    pass