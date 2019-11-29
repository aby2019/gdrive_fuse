import sys,os
import getpass
import re, shutil
import shlex, errno
import difflib, pickle
import drive as model
from tempfile import mkstemp
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle


groot = "/home/hitesh/gdrive0"
gmount = "/home/hitesh/gmount0"

tmpgroot= "/home/hitesh/gdrive"
tmpgmount= "/home/hitesh/gmount"

multiaccount_dict={}

lis= [0] * 50


SCOPES = 'https://www.googleapis.com/auth/drive'

def auth(pickle_file_name):

    pickle_name=str(pickle_file_name)
    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(pickle_name):
        with open(pickle_name, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(pickle_name, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def cd(ip,directory,cur_path_new,service):
    cur_path = cur_path_new
    if ip == "..":
        if not cur_path == groot:
            cur_path = cur_path.rpartition("/")[0]
    elif ip == ".":
        cur_path = cur_path_new
    else:
        cur_path = cur_path_new + "/" +ip
        # print(cur_path)
    if not os.path.isdir(cur_path):
        cur_path = cur_path.rpartition("/")[0]
        print("[ERROR] Not a directory")
        return
    # print(ip)
    # print(cur_path)
    # print(directory[cur_path])

    print(directory)
    directory = model.list(cur_path,directory,service)

    print(directory)

    return directory
    

def rm(ip,directory,service):

    if ip not in directory.keys():
        print("[ERROR] No such file/directory")
        return

    directory = model.trash(ip, directory,service)
    return directory
    

def ls() :
    content = os.listdir(cur_path)
    content.sort()
    for i in content : 
        print(i)

def mkdir(folder_name,directory,cur_path,service):
    if not os.path.isdir(folder_name):
        parent_id = directory[cur_path]
        folder_id = model.create(folder_name, service, parent_id)
        directory[cur_path + '/' + folder_name] = folder_id
    else:
        print("[ERROR] Directory already exists")
    return directory

def move(from_path, to_path,directory,service):

    if from_path not in directory.keys():
        print("[ERROR] Invalid source")
        return

    if to_path not in directory.keys():
        print("[ERROR] Invalid destination")
        return

    if os.path.isfile(to_path):
        print("[ERROR] Destination should be a directory")
        return

    directory = model.move(from_path, to_path, directory,service)

    return directory

    # store()

def copy(from_path, to_path,directory,service):

    if from_path not in directory.keys():
        print("[ERROR] Invalid source")
        return

    if to_path not in directory.keys():
        print("[ERROR] Invalid destination")
        return

    if os.path.isfile(to_path):
        print("[ERROR] Destination should be a directory")
        return

    model.copy(from_path, to_path, directory,service)

def upload(source,destination,directory,service):
    if destination.endswith("/"):
        destination = destination[:-1]
        print(destination)
    if os.path.isdir(destination):
        folder_id = directory[destination]
        if os.path.exists(source):
            filename = source[source.rfind('/')+1:]
            model.upload(source,filename,folder_id,service)
        else:
            print("[ERROR] Invalid source")
    else:
        print("[ERROR] Invalid destination")

def switch(account_id):

    global multiaccount_dict
    global lis

    account_list=[]

    account_id_string = str(account_id)

    service=auth(account_id) #0

    account_list.append(service)

    groot = tmpgroot + account_id_string

    account_list.append(groot) #1

    gmount = tmpgmount + account_id_string

    account_list.append(gmount)#2

    cur_path = groot 

    account_list.append(cur_path)#3

    print(lis[account_id])

    if lis[account_id] == 0:
        directory = { groot : 'root' }
        account_list.append(directory)#4
    else:
        account_list.append(multiaccount_dict[account_id][4])

    if not os.path.isdir(groot):
        os.mkdir(groot,)

    if not os.path.isdir(gmount):
        os.mkdir(gmount)

    multiaccount_dict[account_id]= account_list 



if __name__ == '__main__':

    print("Application Started....") 

    switch(0)

    lis[0]=1

    current= 0 

    service = multiaccount_dict[0][0]

    groot = multiaccount_dict[0][1]

    gmount = multiaccount_dict[0][2]

    cur_path = multiaccount_dict[0][3]

    directory = multiaccount_dict[0][4]

    directory=cd('..',directory,cur_path,service)

    print(directory)

    while True:

        ip = input(">>> ")

        command = ip.split()[0]

        if command == "exit":
            exit()

        if command == "upload":
            print("Uploading "+ ip.split()[1] + " to " + ip.split()[2])
            upload(shlex.split(ip)[1], groot+shlex.split(ip)[2],directory,service)

        if command == "cd":
            directory=cd(shlex.split(ip)[1],directory,cur_path,service) 
            print(directory)

        if command == "rm":
            print("Trashing: " + (cur_path + "/" + shlex.split(ip)[1]))
            directory=rm(cur_path + "/" + shlex.split(ip)[1],directory,service)       

        if command == "ls":
            directory=cd('.',directory,cur_path,service)
            print(directory)
            ls()

        if command == "mkdir":
            directory=mkdir(shlex.split(ip)[1],directory,cur_path,service)

        if command == "move":
            print("Moving " + (cur_path + shlex.split(ip)[1]) + " to " + cur_path + shlex.split(ip)[2])
            directory=move(cur_path + shlex.split(ip)[1], groot + shlex.split(ip)[2],directory,service)

        if command == "copy":
            print("Copying " + (cur_path + shlex.split(ip)[1]) + " to " + cur_path + shlex.split(ip)[2])
            copy(cur_path + shlex.split(ip)[1], groot + shlex.split(ip)[2],directory,service)

        if command == "switch":
           
            print("switching to ")
            
            account_to_switch=0

            account_to_switch = int(ip.split()[1])

            lis[current] = 1

            multiaccount_dict[current][4] = directory

            current = account_to_switch

            switch(account_to_switch)

            service = multiaccount_dict[account_to_switch][0]

            groot = multiaccount_dict[account_to_switch][1]

            gmount = multiaccount_dict[account_to_switch][2]

            cur_path = multiaccount_dict[account_to_switch][3]

            directory = multiaccount_dict[account_to_switch][4]

            print(directory)

