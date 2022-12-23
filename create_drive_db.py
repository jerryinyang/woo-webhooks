from config import Config as config
import shutil

shutil.copyfile(F'./instance/{config.DRIVE_FILE_NAME}', './instance/db.sqlite3')
print('Copied')
