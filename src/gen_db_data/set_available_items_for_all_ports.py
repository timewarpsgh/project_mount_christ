import json
import random

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from world_models import Port, \
    SESSION as WORLD_SESSION


CAPITAL_IDS = {1, 2, 3, 9, 30, 34}
NORMAL_ITEMS_IDS = [
32,
33,
34,
9,
1,
2,
3,
4,
5,
6,
8,
14,
15,
16,
17,
18,
19,
20,
21,
22,
23,
24,
25,
26,
27,
28,
29,
30,
31,
7,
50,
47,
39,
44,
52,
]

def set_available_items_for_all_ports():
    ports = WORLD_SESSION.query(Port).all()

    for port in ports:

        if port.id in CAPITAL_IDS:
            port.items_ids = '1 2 3 4 32 50'
        elif port.id <= 100:
            # give 3 rand items
            ids = random.sample(NORMAL_ITEMS_IDS, 3)
            ids_str = [str(id) for id in ids]
            port.items_ids = ' '.join(ids_str)

    WORLD_SESSION.commit()
    WORLD_SESSION.close()


def main():
    set_available_items_for_all_ports()


if __name__ == '__main__':
    main()