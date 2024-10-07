import json

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')
from world_models import MateTemplate, \
    SESSION as WORLD_SESSION

from role_models import SESSION, Mate


def sync_npc_mates_from_mate_templates():
    mate_templates = WORLD_SESSION.query(MateTemplate).all()
    for mate_template in mate_templates:
        mate = SESSION.query(Mate).filter(Mate.mate_template_id == mate_template.id).first()
        if mate:
            mate.navigation = mate_template.navigation
            mate.accounting = mate_template.accounting
            mate.battle = mate_template.battle

            mate.lv_in_nav = mate_template.lv_in_nav
            mate.lv_in_acc = mate_template.lv_in_acc
            mate.lv_in_bat = mate_template.lv_in_bat

    SESSION.commit()
    SESSION.close()
    WORLD_SESSION.close()


def main():
    sync_npc_mates_from_mate_templates()


if __name__ == '__main__':
    main()