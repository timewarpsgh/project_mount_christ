import sys
import os
import json
import pprint


PATH_TO_DIR = r'D:\data\code\python\project_mount_christ\src\server\models'
sys.path.append(PATH_TO_DIR)

from world_models import SESSION, ItemTemplate

def main():
    d = {}
    mates = SESSION.query(ItemTemplate).all()
    for mate in mates:
        d[mate.description] = ''

    SESSION.close()

    pprint.pprint(d)

if __name__ == '__main__':
    main()