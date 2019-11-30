import sys,os
import getpass
import re, shutil
import io, errno
import difflib, pickle as pickle
import drive
from tempfile import mkstemp
from oauth2client.file import Storage

groot = "/home/abhinav/gdrive"
gmount = "/home/abhinav/gmount"
directory={'/home/abhinav/gdrive': 'root'}
cur_path = groot

def cd(path):
    global directory
    global cur_path
    
    if path == "..":
        if not cur_path == groot:
            cur_path = cur_path.rpartition("/")[0]
    elif path == ".":
        return
    else:
        cur_path = cur_path + "/" +path
        print("current path is",cur_path)
    if not os.path.isdir(cur_path):
        print("error: not a directory")
        while not os.path.isdir(cur_path):
            cur_path = cur_path.rpartition("/")[0]
            print("current path is",cur_path)

            if cur_path == groot: 
                break
        if cur_path[-1]=='/':
            cur_path = cur_path.rpartition("/")[0]
        return
    directory = drive.list(cur_path, directory)

def rm(path):
    global directory

    if path not in directory.keys():
        print("error: No such file or directory")
    else:
        directory = drive.trash(path, directory)

def ex():
    cur_path=groot
    for filename in os.listdir(cur_path):
        file_path = os.path.join(cur_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)           
    exit()

def ls() :
    listoffiles = os.listdir(cur_path)  
    for file in listoffiles : 
        print(file)

def mkdir(name):
    if os.path.isdir(cur_path+'/'+name):
        print("error: directory already exists")
        return
    else:
        parent_id = directory[cur_path]
        folder_id = drive.create_folder(name, parent_id)
        directory[cur_path + '/' + name] = folder_id

def move(source,destination):
    global directory
    if source not in directory.keys():
        print("error: invalid source")
        return
    if destination not in directory.keys():
        print("error: invalid destination")
        return  

    if os.path.isfile(destination):
        print("error: destination should be a directory")
        return
    directory = drive.move(source,destination, directory)

def upload(source,destination):
    global cur_path
    if os.path.isdir(destination):

        folder_id = directory[destination]
        print(destination)  
        if os.path.isfile(source):
            filename = source[source.rfind('/')+1:]
            print(filename)
            drive.upload(source,filename,folder_id)
        else:
            print("error: invalid source")
    else:
        print("error: invalid destination")

if __name__ == '__main__': 
    drive.serv()#initialising 
    directory = drive.list(cur_path, directory)
    while True:

        inp = input("$")
        print(directory.keys())
        command = inp.split()[0]
        if command == "cd":
            cd(inp.split()[1]) 
        elif command == "upload" or command=="copy":
            upload(inp.split()[1],inp.split()[2])

        elif command == "rm":
            print(directory.keys())
            rm(cur_path + "/" + inp.split()[1])       

        elif command == "ls":
            directory = drive.list(cur_path, directory)
            ls()

        elif command == "mkdir":
            mkdir(inp.split()[1])

        elif command == "mv":
            move(cur_path + inp.split()[1], groot + inp.split()[2])

        elif command == "exit":
            ex()
            exit()
        else:
            print("error: wrong input format")
            continue
        