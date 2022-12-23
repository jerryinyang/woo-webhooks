import os

class Config:
    Webhook_Token = '6l7Bb3aCJ1OyCDXd'

    BASE_URL = 'https://api.woo.org'

    API_KEY = 'SNwUjfYcrUlkwqNrc1BGIg=='
    API_SECRET = 'S2MVH3LFA6JZ4CP7Z5YSF2MUIYGM'

    MASTER_1 = "$DNXPJ4FSFIPABAEC957DXG9MKJ62I5EJ392A8HZIBX1P2VQT2L"
    MASTER_2 = "#XD16AEVJ7B1TY9Y7ZWR6DANNXV4CF19LSDXYOQLWZAEJPMCS6U"

    SQLALCHEMY_DATABASE_URI = 'postgresql://uedgnobwseqlvi:730f3190e71765fbbc3563c2a6d30b6356bbd5dca2f44b01a2de6456c1a007d3@ec2-34-242-8-97.eu-west-1.compute.amazonaws.com:5432/de94c9lhft0n26' # os.environ.get('DATABASE_URL') #'sqlite:///db.sqlite3'

    DRIVE_FOLDER_NAME = 'woox-webhook-database'
    DRIVE_FILE_NAME = 'drive_db.sqlite3'

