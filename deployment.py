import os
from client import Client
import logging
import json
import sys
import threading
from pathlib import Path
with open("config.json") as json_data_file:
    config = json.load(json_data_file)
logging.basicConfig(filename=Path(
    config['logLocation']) / 'deployment.log', filemode='w', level=logging.INFO)


# single file single client test
# logging.info("single file download test one client")
# Client( 'n', 's', '4.pdf')
# logging.info("Multi file sequential download test one client")
# Client( 'y', 's', '1.txt,4.pdf')
# logging.info("Multi file parallel download test one client")
# Client( 'y', 'p', '2.txt,4.pdf')

# single file multi client test
i = int(sys.argv[1])
logging.info("single file download test"+ str(i)+ "client start")
j = 1
while(i >= j):
    logging.info("client number "+str(j))
    threading.Thread(target=Client,
                            args=('n', 's', '4.pdf',)).start()
    j = j+1
logging.info("single file download test"+ str(i)+ "client end")
