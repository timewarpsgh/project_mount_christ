from sqlalchemy import Column, Integer, String, Boolean, DateTime, BLOB, create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy

import json


PATH_TO_DB = r'D:\data\code\python\project_mount_christ\data\role_db.sqlite'
BASE = sqlalchemy.orm.declarative_base()


def create_session():
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	Session = sessionmaker(bind=engine)
	session = Session()

	return session


SESSION = create_session()


class Role(BASE):
	# table
	__tablename__ = 'role'

	# id
	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	world_id = Column(Integer)
	account_id = Column(Integer)

	map_id = Column(Integer)
	x = Column(Integer)
	y = Column(Integer)
	dir = Column(Integer)
	money = Column(Integer)
	seen_grids = Column(String)

	discovery_ids_json_str = Column(String)


class Mate(BASE):
	# table
	__tablename__ = 'mate'

	# id
	id = Column(Integer, primary_key=True)
	role_id = Column(Integer)
	npc_id = Column(String)

	name = Column(String)
	img_id = Column(String)
	nation = Column(String)

	lv = Column(Integer)
	points = Column(Integer)
	assigned_duty = Column(String)
	ship_id = Column(Integer)

	leadership = Column(Integer)

	navigation = Column(Integer)
	accounting = Column(Integer)
	battle = Column(Integer)

	talent_in_navigation = Column(Integer)
	talent_in_accounting = Column(Integer)
	talent_in_battle = Column(Integer)


class Ship(BASE):
	# table
	__tablename__ = 'ship'

	# id
	id = Column(Integer, primary_key=True)
	role_id = Column(Integer)
	npc_id = Column(String)

	name = Column(String)
	ship_template_id = Column(Integer)


	material_type = Column(Integer)
	captain = Column(Integer)
	accountant = Column(Integer)
	first_mate = Column(Integer)
	chief_navigator = Column(Integer)

	now_durability = Column(Integer)
	max_durability = Column(Integer)

	tacking = Column(Integer)
	power = Column(Integer)

	capacity = Column(Integer)

	now_crew = Column(Integer)
	min_crew = Column(Integer)
	max_crew = Column(Integer)

	now_guns = Column(Integer)
	type_of_guns = Column(Integer)
	max_guns = Column(Integer)

	water = Column(Integer)
	food = Column(Integer)
	material = Column(Integer)
	cannon = Column(Integer)

	cargo_cnt = Column(Integer)
	cargo_id = Column(Integer)


def create_tables():
	# ceate all above tables if not there yet
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	BASE.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
	create_tables()
