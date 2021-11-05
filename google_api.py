from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from apiclient import errors
from tqdm import tqdm

# If modifying these scopes, delete the file token.json.
SCOPES = [
  'https://www.googleapis.com/auth/drive',
  'https://www.googleapis.com/auth/drive.file',
  'https://www.googleapis.com/auth/drive.appdata',
  'https://www.googleapis.com/auth/drive.scripts',
  'https://www.googleapis.com/auth/drive.metadata'
]

NPY_TO_FUTURE_DELETED_FOLDER = '1eIvby_zsdJt710SlFlTWaAcSMCur5Yfl'
ROOT_FOLDER = '0AA9ojGTiAJchUk9PVA'

class GoogleAPI:
  def __init__ (self):
    super().__init__()

  def authenticate(self):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
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
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds

  def start(self, items):
    self.move_to_parent(items, NPY_TO_FUTURE_DELETED_FOLDER)

  def list_files(self, orderBy=None, query="name contains '.npy'", nextPageToken=None):
    creds = self.authenticate()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
      pageSize=1000,
      orderBy=orderBy,
      pageToken=nextPageToken,
      q="(%s) and trashed = false and '%s' in parents and mimeType != 'application/vnd.google-apps.folder'" % (query, ROOT_FOLDER),
      fields="nextPageToken, files(name,id)"
    ).execute()

    items = results.get('files', [])
    nextPageToken = results.get('nextPageToken', '')
    return items, nextPageToken

  def move_to_parent(self, items, parent):
    creds = self.authenticate()
    service = build('drive', 'v3', credentials=creds)
    if not items:
      print('No files found.')
    else:
      with open('moving.log', 'a') as file_object:
        for index in tqdm(range(len(items))):
          item = items[index]
          file_object.write('[%2d/%d] moving... %s\n' % (index, len(items), item['name']))
          try:
            service.files().update(
              fileId=item['id'],
              addParents=parent,
              removeParents=ROOT_FOLDER,
            ).execute()
          except errors.HttpError as error:
            print('[%s] An error occurred: %s' % (item['name'], error))