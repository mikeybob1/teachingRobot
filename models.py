from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, MetaData, String, Table
from sqlalchemy.orm.base import Mapped

metadata = MetaData()


t_user = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True),
    Column('phoneNumber', String(20)),
    Column('userName', String(20), nullable=False),
    Column('account', String(20), nullable=False),
    Column('icon', String(30))
)

t_aiteacher = Table(
    'aiteacher', metadata,
    Column('id', Integer, primary_key=True),
    Column('time', DateTime, nullable=False),
    Column('plan', String(1000), nullable=False),
    Column('userId', Integer, nullable=False),
    ForeignKeyConstraint(['id'], ['user.id'], name='aiTeacher_FK')
)

t_picture = Table(
    'picture', metadata,
    Column('id', Integer, primary_key=True),
    Column('url', String(100), nullable=False),
    Column('userId', String(100), nullable=False),
    Column('time', DateTime, nullable=False),
    ForeignKeyConstraint(['id'], ['user.id'], name='Picture_FK')
)
