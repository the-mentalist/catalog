from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False)
    password_hash = Column(String(64))

    def hash_password(self, password):
    	self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
    	return pwd_context.verify(password, self.password_hash)


class Catalog(Base):
	__tablename__ = 'catalog'
	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)

class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)
	catalog_id = Column(Integer, ForeignKey('catalog.id'))
	user_id = Column(Integer, ForeignKey('user.id'))
	description = Column(String(250))
	user = relationship(User)
	catalog = relationship(Catalog)

engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
