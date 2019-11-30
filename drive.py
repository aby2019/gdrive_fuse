from __future__ import print_function
from googleapiclient.discovery import build, MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
import io, os
import re, shutil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = 'https://www.googleapis.com/auth/drive'

service=""

def serv():
    global service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    

def list(path, directory):
    # mime_type = ["application/vnd.oasis.opendocument.text",
    # "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","application/x-vnd.oasis.opendocument.spreadsheet",
    # "application/vnd.openxmlformats-officedocument.presentationml.presentation"]
    mime_type = [ "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet", "application/vnd.google-apps.presentation", "application/vnd.google-apps.drawing"]

    temp_directory = []
    folder_id = directory[path]
    results = service.files().list(q="'" + folder_id + "' in parents and trashed=false").execute()

    items = results.get('files', [])
    print(items)


    if not items:
        print('empty Directory')
    else:
        for item in items:
            temp_directory.append(path + '/'+item['name'])
            if item['mimeType'] == "application/vnd.google-apps.folder":
                    if os.path.isdir(path + '/'+item['name']):
                        continue
                    else:
                        os.mkdir(path +'/'+ item['name'])
                        print ("downloaded",item['name'])
                        directory[path + '/'+item['name']] = item['id']
            else:
                if item['mimeType'] in mime_type:
                    download_googledocs(path+'/'+item['name'],item['id'],item['name'],item['mimeType'])              
                else:
                    download(path+'/'+item['name'],item['id'],item['name'])              
            directory[path + '/'+item['name']] = item['id']
                    

        newlist = []

        for item in directory.keys():
            if re.match(path +'/'+ ".*", item):
                newlist.append(item)

        for item in newlist:
            if item not in temp_directory:
                
                del directory[item]

                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)

    return directory
def download_googledocs(file_path,file_id,file_name,mime_type):
    global service
    if mime_type=="application/vnd.google-apps.spreadsheet":
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if not os.path.isfile(file_path):
        request = service.files().export_media(fileId=file_id,mimeType=mime_type)   
    else:
        return              
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print (file_name,"Downloooaded %d%%." % int(status.progress() * 100))

def download(file_path,file_id,filename):
    global service
    if not os.path.isfile(file_path):
        request = service.files().get_media(fileId=file_id)
    else:
        return
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print (filename,"Downloaded %d%%." % int(status.progress() * 100))

    # with io.open(filepath,'wb') as w:
    #     fh.seek(0)
    #     w.write(fh.read())

def create_folder(folder_name, parent_id=None):
    global service
    folder = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        folder['parents'] = [parent_id]

    file = service.files().create(body=folder, fields='id').execute()

    print (folder_name,'  Folder ID: %s' % file.get('id'))

    return file.get('id')


def upload(file_path, file_name, folder_id):
    global service
    file_metadata = {
        'name': file_name,
        'parents' : [folder_id]
    }

    media = MediaFileUpload(file_path)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    # request = service.files().create(media_body=media, body={'name': 'filename'})
    # media.stream() ### this line doesn't exist in the guide... ###
    # response = None
    # while response is None:
    #   status, response = request.next_chunk()
    #   if status:
    #     print ("uploaded %d%%." % int(status.progress() * 100))
    # print ("upload complete")
def move(source, destination, directory):

    global service

    file_id = directory[source]

    folder_id = directory[destination]
    file = service.files().get(fileId=file_id, fields='parents').execute()

    previous_parents = ",".join(file.get('parents'))

    file = service.files().update(fileId=file_id, addParents=folder_id, removeParents=previous_parents, fields='id, parents').execute()

    del directory[source]

    if os.path.isdir(source):
        shutil.rmtree(source)
    else:
        os.remove(source)

    return directory


def trash(path, directory):
    global service

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


def uploadd(filename,filepath,mime): 
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath,
                        mimetype=mime)
    global service
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print ('File ID: %s' % file.get('id'))
