from sqlalchemy import Column, Integer, String, BLOB, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import json

PATH_TO_DB = r'D:\data\code\python\project_mount_christ\data\server_data.sqlite'

Base = declarative_base()


class Account(Base):
	# table
	__tablename__ = 'account'

	# id
	id = Column(Integer, primary_key=True)

	account = Column(String(20))
	password = Column(String(20))


class World(Base):
	# table
	__tablename__ = 'world'

	# id
	id = Column(Integer, primary_key=True)

	name = Column(String(20))


class Role(Base):
	# table
	__tablename__ = 'role'

	# id
	id = Column(Integer, primary_key=True)

	name = Column(String(20))
	data = Column(BLOB)
	world_id = Column(Integer)
	account_id = Column(Integer)


def create_session():
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	Session = sessionmaker(bind=engine)
	session = Session()

	return session


def create_tables():
	# ceate all above tables if not there yet
	engine = create_engine(f'sqlite:///{PATH_TO_DB}')
	Base.metadata.create_all(engine, checkfirst=True)


if __name__ == '__main__':
	create_tables()
