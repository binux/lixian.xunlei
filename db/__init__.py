# -*- encoding: utf-8 -*-

from model import *

from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine(options.database_engine, echo=options.database_echo, pool_recycle=3600)

metadata = Base.metadata
metadata.create_all(engine)

Session = sessionmaker(bind=engine)
