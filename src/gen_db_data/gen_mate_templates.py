import random

# import from dir
import sys
sys.path.append(r'D:\data\code\python\project_mount_christ\src\server\models')

from world_models import create_session, MateTemplate


def rand_one_talent(mate, talent_name):
    chance = random.random()
    if chance < 0.5:
        setattr(mate, talent_name, 0)
    elif chance < 0.8:
        setattr(mate, talent_name, 1)
    elif chance < 0.95:
        setattr(mate, talent_name, 2)
    else:
        setattr(mate, talent_name, 3)


def rand_one_lv(mate, lv):
    lv_int = random.randint(1, 60)
    setattr(mate, lv, lv_int)


def lv_to_target_lv_in_one_field(mate, field):
    target_lv = getattr(mate, f'lv_in_{field[0:3]}')
    talent = getattr(mate, f'talent_in_{field}')

    now_lv = 1

    value_of_field = 1

    while now_lv < target_lv:
        now_lv += 1

        value_of_field += 1

        chance = random.random()
        if chance < 0.5:
            value_of_field += talent

    setattr(mate, field, value_of_field)


def init_mate_templates():
    """
    each mate, init rand talents, init lvs, lv up to these lvs based on talents
    """
    session = create_session()

    mates = session.query(MateTemplate).all()

    for mate in mates:

        # init rand talents
        talents = ['talent_in_navigation', 'talent_in_accounting', 'talent_in_battle']
        for talent in talents:
            rand_one_talent(mate, talent)

        # init lvs
        lvs = ['lv_in_nav', 'lv_in_acc', 'lv_in_bat']
        for lv in lvs:
            rand_one_lv(mate, lv)

        # lv up to these lvs based on talents
        fields = ['navigation', 'accounting', 'battle']
        for field in fields:
            lv_to_target_lv_in_one_field(mate, field)

    session.commit()

    session.close()



def main():
    init_mate_templates()


if __name__ == '__main__':
    main()
