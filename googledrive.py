from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os
import io
from googleapiclient.http import MediaIoBaseDownload

# Authentication
def google_drive_auth(scopes):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Downloading files
def download_file(service, file_id, file_name, folder_path):
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(folder_path, file_name)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    print(f"Downloaded {file_name} to {file_path}")

def list_and_download_files(service, folder_path):
    results = service.files().list(pageSize=100, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
            download_file(service, item['id'], item['name'], folder_path)

# Main function
def main():
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = google_drive_auth(SCOPES)
    service = build('drive', 'v3', credentials=creds)
    download_folder_path = 'path/to/your/local/folder'
    list_and_download_files(service, download_folder_path)

if __name__ == '__main__':
    main()
