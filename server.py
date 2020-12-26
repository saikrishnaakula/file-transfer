import socket
import threading
import os
import hashlib
import json
from pathlib import Path
import logging
import time

class Server:
    def __init__(self):
        with open("./config.json") as json_data_file:
            self.config = json.load(json_data_file)
        self.dataFolder = Path(self.config['hostedFolder'])
        logging.basicConfig(filename=Path(
            self.config['logLocation']) / 'server.log', filemode='w', level=logging.INFO)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.accept_connections()

    def md5(self, name):
        hash_md5 = hashlib.md5()
        with open(name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def accept_connections(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = self.config["port"]
        self.s.bind((ip, port))
        self.s.listen(600)
        # logging.info('Running on IP: '+ip)
        # logging.info('Running on port: '+str(port))

        while 1:
            c, addr = self.s.accept()
            # logging.info('Client registered '+str(addr))
            threading.Thread(target=self.handle_client,
                             args=(c, addr,)).start()

    def handle_client(self, c, addr):
        while True:
            data = c.recv(1024).decode()
            if(data == 'listoffiles'):
                logging.info('Sent list of files to '+str(addr))
                files = os.listdir(self.dataFolder)
                files = str(files)
                files = files.encode()
                c.sendall(files)
                continue

            if(data == 'md5'):
                c.sendall("fileName".encode())
                c.sendall(self.md5(self.dataFolder /
                                   c.recv(1024).decode()).encode())
                logging.info('md5 token sent to '+str(addr))
                continue

            if(data == 'downloadfile'):
                c.sendall("fileName".encode())
                data = c.recv(1024).decode()
                filePath = self.dataFolder / data
                fileSize = str(os.path.getsize(filePath))
                logging.info('download requested for file ' +
                             data + ' size ' + fileSize
                                  + 'Bytes by '+str(addr))
                if not os.path.exists(filePath):
                    logging.info('file doesnt exit '+data + ' to '+str(addr))
                    c.sendall("file-doesn't-exist".encode())
                else:
                    c.sendall(fileSize.encode())
                    logging.info('sending file '+data + ' to '+str(addr))
                    if data != '':
                        tic = time.perf_counter()
                        file = open(filePath, 'rb')
                        fdata = file.read(1024)
                        while fdata:
                            c.sendall(fdata)
                            fdata = file.read(1024)
                        file.close()
                        toc = time.perf_counter()
                        totalTime = str(f"{toc - tic:0.4f} seconds")
                        # print(totalTime)
                        logging.info('file '+data + ' sent in ' + totalTime +' to '+str(addr))
                        # logging.info(totalTime)
                        # c.shutdown(socket.SHUT_RDWR)
                        # c.close()
                        continue


server = Server()
