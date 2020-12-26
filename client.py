import socket
import os
import hashlib
from pathlib import Path
import json
import threading


class Client:

    def __init__(self,multiple,parallel,fileName):
        with open("config.json") as json_data_file:
            self.config = json.load(json_data_file)
        self.downloadFolder = Path(self.config['downloadLocation'])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.multiple = multiple
        self.parallel = parallel
        self.file_name = fileName
        self.connect_to_server()

    def connect_to_server(self):

        # self.name = 'sai'  # input("client name -->")
        self.target_ip = socket.gethostbyname(socket.gethostname())
        self.target_port = self.config["port"]
        self.s.connect((self.target_ip, int(self.target_port)))
        self.main()

    def reconnect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.target_ip, int(self.target_port)))

    def md5(self, name):
        hash_md5 = hashlib.md5()
        with open(name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def downloadFileSingle(self, file_name):
        self.s.sendall('md5'.encode())
        if self.s.recv(1024).decode() == 'fileName':
            self.s.sendall(file_name.encode())
        hash = self.s.recv(1024).decode()
        print(hash)
        self.s.sendall('downloadfile'.encode())
        if self.s.recv(1024).decode() == 'fileName':
            self.s.sendall(file_name.encode())
        size = self.s.recv(1024).decode()
        if size == "file-doesn't-exist":
            print("File doesn't exist on server.")
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
        else:
            total = 0
            size = int(size)
            savingFileName = str(self.s.getsockname()[1])+'-'+file_name
            name = self.downloadFolder / savingFileName
            with open(name, 'wb') as file:
                while 1:
                    data = self.s.recv(1024)
                    total = total + len(data)
                    file.write(data)
                    if total >= size:
                        break
                file.close()
            if hash == self.md5(name):
                print(file_name, 'successfully downloaded.')
            else:
                print(file_name, 'unsuccessfully downloaded.')
                if self.counter <= 3:
                    self.downloadFileSingle(file_name)
                    self.counter = self.counter+1

    def parallelDownload(self, file_name):
        childS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        childS.connect((self.target_ip, int(self.target_port)))
        childS.sendall('md5'.encode())
        if childS.recv(1024).decode() == 'fileName':
            childS.sendall(file_name.encode())
        hash = childS.recv(1024).decode()
        print(hash)
        childS.sendall('downloadfile'.encode())
        if childS.recv(1024).decode() == 'fileName':
            childS.sendall(file_name.encode())
        size = childS.recv(1024).decode()
        if size == "file-doesn't-exist":
            print("File doesn't exist on server.")
            childS.shutdown(socket.SHUT_RDWR)
            childS.close()
        else:
            total = 0
            size = int(size)
            savingFileName = str(self.s.getsockname()[1])+'-'+file_name
            name = self.downloadFolder / savingFileName
            with open(name, 'wb') as file:
                while 1:
                    data = childS.recv(1024)
                    total = total + len(data)
                    file.write(data)
                    if total >= size:
                        break
                file.close()
            if hash == self.md5(name):
                print(file_name, 'successfully downloaded.')
            else:
                print(file_name, 'unsuccessfully downloaded.')
        childS.shutdown(socket.SHUT_RDWR)
        childS.close()

    def main(self):
        print("List of files available for download:")
        self.s.send("listoffiles".encode())
        data = self.s.recv(1024).decode()
        for d in eval(data):
            print(d)
        if self.multiple == 0:    
            multiple = input("Do you want to download multiple files (y/n) -->")
        else:
            multiple = self.multiple
        if multiple == 'y' or multiple == 'Y':
            self.counter = 0
            if self.parallel == 0:
                parallel = input("Do you want to download files parallel/seuential(p/s) --> ")
                file_name = input('Enter the file names by comma seperation --> ')
            else:
                parallel =self.parallel
                file_name = self.file_name
            files = file_name.split(",")
            if parallel == 's':
                for f in files:
                    self.downloadFileSingle(f)
            else:
                for f in files:
                    threading.Thread(target=self.parallelDownload,
                                     args=(f,)).start()
        else:
            self.counter = 0
            if self.file_name == 0:
                file_name = input('Enter the file name --> ')
            else:
                file_name = self.file_name
            self.downloadFileSingle(file_name)
        # self.s.shutdown(socket.SHUT_RDWR)
        # self.s.close() 

# client = Client(0,0,0)
