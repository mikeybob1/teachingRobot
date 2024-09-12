from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Date, Integer, DateTime, ForeignKeyConstraint

db = SQLAlchemy()

#创建模型
class Student(db.Model):
    # 表的名字
    __tablename__ = 'tab_student'

    # 表的结构
    sno = Column(String(4), primary_key=True)
    sname = Column(String(10))
    ssex = Column(String(2))
    birthday = Column(Date)
    sclass = Column(String(10))
    grade = Column(Integer)
    majoyno = Column(String(4))


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    phoneNumber = Column(String(20))
    userName = Column(String(20), nullable=False)
    account = Column(String(20), nullable=False)
    icon = Column(String(30))


class AiTeacher(db.Model):
    __tablename__ = 'aiteacher'

    # 正确的主键定义
    id = Column(Integer, primary_key=True)  # 去掉逗号
    time = Column(DateTime, nullable=False)
    plan = Column(String(1000), nullable=False)
    userId = Column(Integer, nullable=False)

    # 外键约束
    ForeignKeyConstraint(['userId'], ['user.id'], name='aiTeacher_FK')
class Picture(db.Model):
    __tablename__ = 'picture'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    url = Column(String(100), nullable=False)
    userId = Column(Integer, nullable=False)
    ForeignKeyConstraint(['id'], ['user.id'], name='Picture_FK')
