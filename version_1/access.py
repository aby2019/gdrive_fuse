import sys,os
import getpass
import re, shutil
import shlex, errno
import difflib, pickle
import drive as model
from tempfile import mkstemp
import pickle

groot = "/home/hitesh/gdrive"
gmount = "/home/hitesh/gmount"
directory = {}
cur_path = groot

def load():
    global directory
    try:
        directory_pckl = open("directory.txt","rb")
        if(os.stat("directory.txt").st_size != 0):
            directory = pickle.load(directory_pckl)
        else:
            directory = { groot : 'root' }
        directory_pckl.close()
    except:
        directory = { groot : 'root' }
        with open('directory.txt', 'wb') as f:
            pickle.dump(directory, f)

def store():
    global directory
    directory_pckl = open("directory.txt","wb")
    pickle.dump(directory, directory_pckl)
    directory_pckl.close()

def cd(ip):
    global directory
    global cur_path
    
    if ip == "..":
        if not cur_path == groot:
            cur_path = cur_path.rpartition("/")[0]
    elif ip == ".":
        cur_path = cur_path
    else:
        cur_path = cur_path + "/" +ip
        # print(cur_path)
    if not os.path.isdir(cur_path):
        cur_path = cur_path.rpartition("/")[0]
        print("[ERROR] Not a directory")
        return
    # print(ip)
    # print(cur_path)
    # print(directory[cur_path])
    directory = model.list(cur_path, directory)
    store()

def rm(ip):
    global directory

    if ip not in directory.keys():
        print("[ERROR] No such file/directory")
        return

    directory = model.trash(ip, directory)
    store()

def ls() :
    content = os.listdir(cur_path)
    content.sort()
    for i in content : 
        print(i)

def mkdir(folder_name):
    if not os.path.isdir(folder_name):
        parent_id = directory[cur_path]
        folder_id = model.create(folder_name, parent_id)
        directory[cur_path + '/' + folder_name] = folder_id
    else:
        print("[ERROR] Directory already exists")

def move(from_path, to_path):
    global directory

    if from_path not in directory.keys():
        print("[ERROR] Invalid source")
        return

    if to_path not in directory.keys():
        print("[ERROR] Invalid destination")
        return

    if os.path.isfile(to_path):
        print("[ERROR] Destination should be a directory")
        return

    directory = model.move(from_path, to_path, directory)

    store()

def copy(from_path, to_path):
    global directory

    if from_path not in directory.keys():
        print("[ERROR] Invalid source")
        return

    if to_path not in directory.keys():
        print("[ERROR] Invalid destination")
        return

    if os.path.isfile(to_path):
        print("[ERROR] Destination should be a directory")
        return

    model.copy(from_path, to_path, directory)

def upload(source,destination):
    if destination.endswith("/"):
        destination = destination[:-1]
        print(destination)
    if os.path.isdir(destination):
        folder_id = directory[destination]
        if os.path.exists(source):
            filename = source[source.rfind('/')+1:]
            model.upload(source,filename,folder_id)
        else:
            print("[ERROR] Invalid source")
    else:
        print("[ERROR] Invalid destination")

if __name__ == '__main__':

    if not os.path.isdir(groot):
        os.mkdir(groot)

    if not os.path.isdir(gmount):
        os.mkdir(gmount)

    load()
    store()
    cd('..')

    while True:

        ip = input(">>> ")

        command = ip.split()[0]

        if command == "exit":
            store()
            exit()

        if command == "upload":
            print("Uploading "+ ip.split()[1] + " to " + ip.split()[2])
            upload(shlex.split(ip)[1], groot+shlex.split(ip)[2])

        if command == "cd":
            cd(shlex.split(ip)[1]) 

        if command == "rm":
            print("Trashing: " + (cur_path + "/" + shlex.split(ip)[1]))
            rm(cur_path + "/" + shlex.split(ip)[1])       

        if command == "ls":
            cd('.')
            ls()

        if command == "mkdir":
            mkdir(shlex.split(ip)[1])

        if command == "move":
            print("Moving " + (cur_path + shlex.split(ip)[1]) + " to " + cur_path + shlex.split(ip)[2])
            move(cur_path + shlex.split(ip)[1], groot + shlex.split(ip)[2])

        if command == "copy":
            print("Copying " + (cur_path + shlex.split(ip)[1]) + " to " + cur_path + shlex.split(ip)[2])
            copy(cur_path + shlex.split(ip)[1], groot + shlex.split(ip)[2])

        store()
