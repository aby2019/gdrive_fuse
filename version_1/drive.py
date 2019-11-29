from __future__ import print_function
from googleapiclient.discovery import build, MediaFileUpload
from googleapiclient.http import    MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
import io, os
import re, shutil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = 'https://www.googleapis.com/auth/drive'

mimeTypes = [ "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet", "application/vnd.google-apps.presentation", "application/vnd.google-apps.drawing"]

pickle_name="0"

def list(path, directory,service):

    temp_directory = []

    folder_id = directory[path]

    results = service.files().list(q="'" + folder_id + "' in parents and trashed=false").execute()

    items = results.get('files', [])

    if not path.endswith('/'):
        path = path + "/"

    if not items:
        print('Empty Directory')
    else:
        for item in items:
            temp_directory.append(path + item['name'])
            if item['mimeType'] == "application/vnd.google-apps.folder":
                    if not os.path.isdir(path + item['name']):
                        os.mkdir(path + item['name'])
                        print("[DOWNLOADED] " + item['name'])
                        directory[path + item['name']] = item['id']
            else:
                flag = False
                if item['mimeType'] in mimeTypes:
                    if not os.path.isfile(path + item['name']):
                        request = service.files().export_media(fileId=item['id'], mimeType='application/pdf')
                        flag = True
                else:
                    if not os.path.isfile(path + item['name']):
                        request = service.files().get_media(fileId=item['id'])
                        flag = True

                if flag:
                    directory[path + item['name']] = item['id']
                    fh = io.FileIO(path+item['name'], 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print('[DOWNLOADED] ' + item['name'])

        newlist = []

        for item in directory.keys():
            if re.match(path + ".*", item):
                newlist.append(item)

        for item in newlist:
            if item not in temp_directory:
                
                del directory[item]

                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)

    return directory

def create(folder_name, service,parent_id=None):

    folder = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        folder['parents'] = [parent_id]

    file = service.files().create(body=folder, fields='id').execute()

    print('[SUCCESS] Folder Created')

    return file.get('id')


def upload(file_path, file_name, folder_id,service):

    file_metadata = {
        'name': file_name,
        'parents' : [folder_id]
    }

    media = MediaFileUpload(file_path)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

def copy(from_path, to_path, directory):

    folder_id = directory[to_path]

    file_name = from_path[from_path.rfind('/')+1:]

    upload(from_path, file_name, folder_id)

def move(from_path, to_path, directory,service):

    file_id = directory[from_path]

    folder_id = directory[to_path]

    file = service.files().get(fileId=file_id, fields='parents').execute()

    previous_parents = ",".join(file.get('parents'))
    print(previous_parents)
    file = service.files().update(fileId=file_id, addParents=folder_id, removeParents=previous_parents, fields='id, parents').execute()

    del directory[from_path]

    if os.path.isdir(from_path):
        shutil.rmtree(from_path)
    else:
        os.remove(from_path)

    return directory


def trash(path, directory,service):

    file_id = directory[path]

    file_metadata = {
        'trashed': 'true'
    }

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

    del directory[path]

    file = service.files().update(body=file_metadata, fileId=file_id).execute()

    return directory


def download(file_id, filename,service):
    
    request = service.files().get_media(fileId=file_id)

    fh = io.FileIO(filename, 'wb')

    downloader = MediaIoBaseDownload(fh, request)

    done = False

    while done is False:
        status, done = downloader.next_chunk()
        print('[DOWNLOADED] ' + filename)