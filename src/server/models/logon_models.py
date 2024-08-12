from sqlalchemy import Column, Integer, String, Boolean, DateTime, BLOB, create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy

import json


PATH_TO_DB = r'D:\data\code\python\project_mount_christ\data\logon_db.sqlite'
BASE = sqlalchemy.orm.declarative_base()


def create_session():
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	Session = sessionmaker(bind=engine)
	session = Session()

	return session


SESSION = create_session()


class Account(BASE):
	# table
	__tablename__ = 'account'

	# id
	id = Column(Integer, primary_key=True)

	account = Column(String(20))
	password = Column(String(20))
	gm_lv = Column(Integer)


class World(BASE):
	# table
	__tablename__ = 'world'

	# id
	id = Column(Integer, primary_key=True)

	name = Column(String(20))




def create_tables():
	# ceate all above tables if not there yet
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	BASE.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
	create_tables()
