# -*- encoding: utf-8 -*-

import sqlalchemy.types as types
from sqlalchemy import *
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MySQLSettings(object):
    __table_args__ = {
        #'mysql_engine'    : 'InnoDB',
        'mysql_engine'    : 'MyISAM',
        'mysql_charset'   : 'utf8',
        }

class Set(types.TypeDecorator):
    """
    自定义类型模板：set
    基础类型：text
    保存格式：key1|key2|key3
    """
    impl = types.Text

    def process_bind_param(self, value, dialect):
        if isinstance(value, basestring):
            return value
        return u"|".join(set(value))

    def process_result_value(self, value, dialect):
        return set(value.split("|"))

class Task(Base, MySQLSettings):
    __tablename__ = "task"

    id = Column(Integer(32), primary_key=True) #same as xunlei task id
    createtime = Column(DateTime, default=func.now(), index=True)
    updatetime = Column(DateTime, default=func.now(), server_onupdate=text("NOW()"))
    create_uid = Column(Integer(32))
    #creator = Column(String(1024))
    tags = Column(Set, default=[])

    cid = Column(String(256), index=True)
    url = Column(String(1024))
    lixian_url = Column(String(1024))
    taskname = Column(String(1024), default="") #
    task_type = Column(String(56))
    status = Column(String(56), index=True)
    process = Column(Float)
    size = Column(Integer(32))
    format = Column(String(56))

    files = relationship("File", cascade="merge")

class File(Base, MySQLSettings):
    __tablename__ = "file"

    id = Column(Integer(32), primary_key=True) #same as xunlei task id
    task_id = Column(Integer(32), ForeignKey("task.id"))
    createtime = Column(DateTime, default=func.now())
    updatetime = Column(DateTime, default=func.now(), server_onupdate=text("NOW()"))

    cid = Column(String(256))
    url = Column(String(1024))
    lixian_url = Column(String(1024))
    title = Column(String(1024), default="") #
    dirtitle = Column(String(1024), default="") #
    status = Column(String(56))
    process = Column(Float)
    size = Column(Integer(32))
    format = Column(String(56))

    task = relationship("Task", cascade="merge")
