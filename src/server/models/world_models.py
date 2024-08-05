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

def create_tables():
	# ceate all above tables if not there yet
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	BASE.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
	create_tables()
