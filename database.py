import sys
from sqlalchemy import Column, ForeignKey, Integer, String, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import backref
#from sqlalchemy_imageattach.entity import Image, image_attachment

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
    # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    picture = Column(BLOB)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(
        Category, backref=backref('children', cascade='all,delete'))

    @property
    def serialize(self):
    # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'picture': self.picture,
            'category_id': self.category_id,
            }

engine = create_engine('sqlite:///categories.db')

Base.metadata.create_all(engine)
