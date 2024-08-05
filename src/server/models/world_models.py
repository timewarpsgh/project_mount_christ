from sqlalchemy import Column, Integer, String, Boolean, DateTime, BLOB, create_engine
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
	nation = Column(String)
	lv = Column(Integer)

	navigation = Column(Integer)
	accounting = Column(Integer)
	battle = Column(Integer)

	talent_in_navigation = Column(Integer)
	talent_in_accounting = Column(Integer)
	talent_in_battle = Column(Integer)


class CargoTemplate(BASE):

	__tablename__ = 'cargo_template'

	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	cargo_type = Column(String(20))
	buy_price = Column(String)  #[market_id_0: 10, market_id_1: 20, ]
	sell_price = Column(String)  #	[1, 2, 3, 4, 5]

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


def create_tables():
	# ceate all above tables if not there yet
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	BASE.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
	create_tables()
