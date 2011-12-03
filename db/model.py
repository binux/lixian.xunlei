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
    保存格式：|key1|key2|key3|
    """
    impl = types.Text

    def process_bind_param(self, value, dialect):
        if isinstance(value, basestring):
            return value
        return "|%s|" % u"|".join(set(value))

    def process_result_value(self, value, dialect):
        return set((x for x in value.split("|") if x))

class Task(Base, MySQLSettings):
    __tablename__ = "task"

    id = Column(BigInteger, primary_key=True) #same as xunlei task id
    createtime = Column(DateTime, default=func.now(), index=True)
    updatetime = Column(DateTime, default=func.now(), server_onupdate=text("NOW()"))
    create_uid = Column(BigInteger)
    creator = Column(String(512))
    tags = Column(Set, default=[])
    invalid = Column(Boolean, default=False)

    cid = Column(String(256), index=True)
    url = Column(String(1024))
    lixian_url = Column(String(1024))
    taskname = Column(String(512), default="", index=True) #
    task_type = Column(String(56))
    status = Column(String(56), index=True)
    process = Column(Float)
    size = Column(BigInteger)
    format = Column(String(56))

    files = relationship("File", cascade="merge", backref=backref("task", cascade="merge"))

class File(Base, MySQLSettings):
    __tablename__ = "file"

    id = Column(BigInteger, primary_key=True) #same as xunlei task id
    task_id = Column(BigInteger, ForeignKey("task.id"))
    createtime = Column(DateTime, default=func.now())
    updatetime = Column(DateTime, default=func.now(), server_onupdate=text("NOW()"))

    cid = Column(String(256))
    url = Column(String(1024))
    _lixian_url = Column("lixian_url", String(1024))
    lixian_url = ""
    title = Column(String(1024), default="") #
    dirtitle = Column(String(1024), default="") #
    status = Column(String(56))
    process = Column(Float)
    size = Column(BigInteger)
    format = Column(String(56))

class User(Base, MySQLSettings):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(512), index=True)
    name = Column(String(256))
    group = Column(String(64))
    permission = Column(Integer)
