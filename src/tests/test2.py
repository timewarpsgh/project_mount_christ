import sys
import os
import json
import pprint


PATH_TO_DIR = r'D:\data\code\python\project_mount_christ\src\server\models'
sys.path.append(PATH_TO_DIR)

from world_models import SESSION, Village

def main():
    d = {}
    entries = SESSION.query(Village).all()
    for entry in entries:
        d[entry.description] = ''

    SESSION.close()

    pprint.pprint(d)

    print(len(d))
if __name__ == '__main__':
    main()