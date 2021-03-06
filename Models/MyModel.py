# -*- coding: utf-8 -*- 
"""
Project: MyProManagent
Author: guokaikuo
Create time: 2021-05-27 10:15
IDE: PyCharm
"""
import pymysql
from sqlalchemy import Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Integer, String, TIMESTAMP, Text, ForeignKey
from Conf import conf

pymysql.install_as_MySQLdb()
engine = create_engine(
    conf.MYSQL_SETTING, pool_size=20, max_overflow=0, pool_recycle=3600)

DBSession = sessionmaker(bind=engine)  # 创建DBSession类型:类似数据库连接
BaseModel = declarative_base()


# 操作日志
class OperateLog(BaseModel):
    __tablename__ = 'operate_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36))
    log_id = Column(String(36))
    file_id = Column(String(36))
    # 添加外键，operate_type不能设置id自增
    type = Column(String(12), ForeignKey('operate_type.type'))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    datetime = Column(TIMESTAMP)
    user = relationship("User", backref="user_of_operate_log")
    operate_type = relationship("OperateType", backref="type_of_operate_log")

    # 将读取的数据和转化成字典
    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


# 用户
class User(BaseModel):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(32))

    def to_dict(self):  # 将读取的数据和转化成字典
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


# 操作类型
class OperateType(BaseModel):
    __tablename__ = 'operate_type'

    type = Column(String(12), primary_key=True)
    type_name = Column(String(32))

    def to_dict(self):  # 将读取的数据和转化成字典
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


# 检测结果
class CheckRes(BaseModel):
    __tablename__ = 'check_res'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36))
    content = Column(Text)
    operate_log_id = Column(Integer, ForeignKey('operate_log.id'))
    operate_log = relationship("OperateLog", backref="detail_of_operate_log")
    # 检测上报时间点
    datetime = Column(TIMESTAMP)

    def to_dict(self):  # 将读取的数据和转化成字典
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


# 检测规则包
class CheckRule(BaseModel):
    __tablename__ = 'check_rule'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(Integer, ForeignKey('rule_type.rule_type'))
    rule_name = Column(String(256))

    # 1、头尾
    head = Column(Text)
    tail = Column(Text)
    # 2、整体完整
    overall_include = Column(Text)
    # 3、文件
    file_include = Column(Text)
    # 4、顺序
    context_pre = Column(Text)
    context_back = Column(Text)
    # 5、区域时限
    part = Column(Text)
    partial_time = Column(Integer)

    rule = relationship("RuleType", backref="rule_of_rule_type")
    datetime = Column(TIMESTAMP)

    def to_dict(self):  # 将读取的数据和转化成字典
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


# 检测规则的类型
class RuleType(BaseModel):
    __tablename__ = 'rule_type'

    rule_type = Column(Integer, primary_key=True)
    type_name = Column(String(32))

    def to_dict(self):  # 将读取的数据和转化成字典
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


def init_db():
    """生成数据表"""
    BaseModel.metadata.create_all(engine)


def drop_db():
    """删除数据表"""
    BaseModel.metadata.drop_all(engine)


if __name__ == '__main__':
    init_db()
