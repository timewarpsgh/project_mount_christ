import sys
import os
import json


PATH_TO_DIR = r'D:\data\code\python\project_mount_christ\src\server\models'
sys.path.append(PATH_TO_DIR)

from world_models import SESSION, Village

def main():
    villages = SESSION.query(Village).all()
    for village in villages:
        description = village.description
        modified_desc = description.replace('’', '\'')
        village.description = modified_desc

    SESSION.commit()
    SESSION.close()



if __name__ == '__main__':
    main()