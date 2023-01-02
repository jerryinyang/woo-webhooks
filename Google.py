import os.path
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import asyncio

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

MIME_TYPES = {
    'folder' : 'application/vnd.google-apps.folder',
    'others' : 'application/vnd.google-apps.unknown',
    'text' : 'text/plain',
    'csv' : 'text/csv',
    'sqlite3' : 'application/vnd.sqlite3'
}

async def Create_Service():
    """
    Creates a service instance for connecting with Google Drive API.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return None

async def Create_Folder(service, name : str):
    """
    Creates a folder in the root Google Drive Folder.
    """

    try:
        folder_exists = await Search_File(service, name, True)

        if folder_exists is not None:
            return folder_exists

        file_metadata = {
                'name': name,
                'mimeType': MIME_TYPES['folder']
            }

        file = service.files().create(body=file_metadata, fields='id').execute()
        print(F'Folder ID: "{file.get("id")}".')

        return file.get('id')

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return None

async def Search_File(service, name : str, isFolder = False):
    """
    Searches the root Google Drive directory for a folder name, and returns its ID, or 'None' if the folder doesn't exist.
    """
    _q = f"name='{name}' and mimeType = 'application/vnd.google-apps.folder'" if isFolder else \
        f"name='{name}' and mimeType != 'application/vnd.google-apps.folder'"

    try:
        files = []
        page_token = None

        while True:
            response = service.files().list(q=_q,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                    'files(id, name)',
                                            pageToken=page_token).execute()

            for file in response.get('files', []):
                # Process change
                if file.get("name") == name:
                    return file.get("id")

                print(F'Found file: {file.get("name")}, {file.get("id")}')


            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)

            if page_token is None:
                return None
        
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return None

async def Upload_File(service, folder_name : str, file_name: str, file_path : str, mimeType : str):
    
    try:
        folder_id = await Create_Folder(service, folder_name)
        media = MediaFileUpload(file_path, mimetype=MIME_TYPES[mimeType], resumable=True)

        file_exist = await Search_File(service, file_name, False)
        
        if file_exist is not None:
            # Update the File
            service.files().update(fileId=file_exist, media_body=media).execute()
            print('Upload Successful')
            return file_exist

        # Create a New File
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()

        return file.get('id')

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
        return None

async def Download_File(service, file_name : str):
    try:
        file_id = await Search_File(service, file_name, False)

        if file_id is not None:
            request = service.files().get_media(fileId=file_id)
            file = io.BytesIO()

            downloader = MediaIoBaseDownload(file, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

            file.seek(0)

            with open(os.path.join('./database', file_name), 'wb') as f:
                f.write(file.read())
                f.close()
                return True
            
        else:
            return None

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None




