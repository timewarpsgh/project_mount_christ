from sqlalchemy import Column, Integer, String, Boolean, DateTime, BLOB, create_engine, Float
from sqlalchemy.orm import sessionmaker
import sqlalchemy

import json


PATH_TO_DB = r'D:\data\code\python\project_mount_christ\data\world_db.sqlite'
BASE = sqlalchemy.orm.declarative_base()


def create_session():
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	Session = sessionmaker(bind=engine)
	session = Session()

	return session


SESSION = create_session()


class Port(BASE):

	__tablename__ = 'port'

	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	x = Column(Integer)
	y = Column(Integer)

	maid_id = Column(Integer)
	mate_id = Column(Integer)

	economy = Column(Integer)
	industry = Column(Integer)

	invest_from_nations = Column(String)

	region_id = Column(Integer)
	economy_id = Column(Integer)
	industry_id = Column(Integer)
	items_ids = Column(String)

	building_locations = Column(String)

	tile_set = Column(Integer)
	governer_role_id = Column(Integer)

	specialty_id = Column(Integer)
	specialty_price = Column(Integer)
	wine = Column(String)


class Maid(BASE):
	# table
	__tablename__ = 'maid'

	# id
	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	img_id = Column(String(20))


class MateTemplate(BASE):
	# table
	__tablename__ = 'mate_template'

	# id
	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	img_id = Column(String(20))
	nation = Column(Integer)

	navigation = Column(Integer)
	accounting = Column(Integer)
	battle = Column(Integer)

	talent_in_navigation = Column(Integer)
	talent_in_accounting = Column(Integer)
	talent_in_battle = Column(Integer)

	lv_in_nav = Column(Integer)
	lv_in_acc = Column(Integer)
	lv_in_bat = Column(Integer)


class CargoTemplate(BASE):

	__tablename__ = 'cargo_template'

	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	cargo_type = Column(String(20))
	buy_price = Column(String)
	sell_price = Column(String)

	required_economy_value = Column(Integer)


class ShipTemplate(BASE):
	__tablename__ = 'ship_template'

	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	img_id = Column(String(20))

	durability = Column(Integer)

	tacking = Column(Integer)
	power = Column(Integer)

	capacity = Column(Integer)
	max_guns = Column(Integer)
	min_crew = Column(Integer)
	max_crew = Column(Integer)
	buy_price = Column(Integer)

	required_industry_value = Column(Integer)
	lv = Column(Integer)


class ItemTemplate(BASE):

	__tablename__ = 'item_template'

	id = Column(Integer, primary_key=True)

	name = Column(String)
	description = Column(String)
	img_id = Column(String)

	item_type = Column(String)

	buy_price = Column(Integer)
	effect = Column(Integer)
	lv = Column(Integer)


class Cannon(BASE):

	__tablename__ = 'cannon'

	id = Column(Integer, primary_key=True)

	name = Column(String)
	price = Column(Integer)
	damage = Column(Float)


class Village(BASE):

	__tablename__ = 'village'

	id = Column(Integer, primary_key=True)

	name = Column(String)
	description = Column(String)
	img_id = Column(String)

	x = Column(Integer)
	y = Column(Integer)
	latitude = Column(String)
	longitude = Column(String)

	navigation_required = Column(Integer)
	item_id_2_drop_rate = Column(String)


class Npc(BASE):

	__tablename__ = 'npc'

	id = Column(Integer, primary_key=True)
	mate_id = Column(Integer)

	x = Column(Integer)
	y = Column(Integer)
	dir = Column(Integer)
	map_id = Column(Integer)


class Aura(BASE):

	__tablename__ = 'aura'

	id = Column(Integer, primary_key=True)

	name = Column(String)
	description = Column(String)


class Event(BASE):

	__tablename__ = 'event'

	id = Column(Integer, primary_key=True)

	port = Column(String)
	building = Column(String)
	figure_images = Column(String)
	dialogues = Column(String)
	reward_type = Column(String)
	reward_id = Column(Integer)
	lv = Column(Integer)


def create_tables():
	# ceate all above tables if not there yet
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	BASE.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
	create_tables()
