from Google import *
import asyncio
import time
from config import Config as config

service = asyncio.run(Create_Service())

if service is not None:
    # print(asyncio.run(Create_Folder(service, 'Test Folder')))
    # print(Search_File(service, 'Test Folder'))
    # print(asyncio.run(Upload_File(service, 'Test Folder', 'db', './instance/db.sqlite3', 'sqlite3')))
    print(asyncio.run(Download_File(service, config.DRIVE_FILE_NAME)))
    pass

# x = 10

# def func_1(x, y):
#     try:
#         z = x + y
#         return z
#     except Exception as e:
#         return e

#     finally:
#         count = 10

#         while count < 10000000000:
#             count += 1
#         x = 20
#         print(x)

# def func_2():
#     print( func_1(3, 4) )

# func_2()



# async def main():
#     f1 = asyncio.create_task(function_1())
#     f2 = asyncio.create_task(function_2())
#     await asyncio.wait([f1, f2])

# asyncio.run(main())

# count = 20
# while count < 40:
#     print(count)
#     time.sleep(.5)
#     count += 1