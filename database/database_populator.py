from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Catalog, Item, engine, Base

Base.metadata.bind = engine

# A DBSession() instance establishes all conversations with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user1 = User(email = 'admin')
user1.hash_password('123654')
session.add(user1)
session.commit()

# Sample Catalogs
Soccer = Catalog(name = 'Soccer')
session.add(Soccer)

Baseball = Catalog(name = 'Baseball')
session.add(Baseball)

Basketball = Catalog(name = 'Basketball')
session.add(Basketball)

Frisbee = Catalog(name = 'Frisbee')
session.add(Frisbee)

Snowboarding = Catalog(name = 'Snowboarding')
session.add(Snowboarding)

Rockclimbing = Catalog(name = 'Rock Climbing')
session.add(Rockclimbing)

Foosball = Catalog(name = 'Foosball')
session.add(Foosball)

Skating = Catalog(name = 'Skating')
session.add(Skating)

Hockey = Catalog(name = 'Hockey')
session.add(Hockey)

session.commit()

# Sample Items
Stick = Item(name='Stick', catalog_id=9, user_id=1)
session.add(Stick)

Goggles = Item(name='Goggles', catalog_id=5, user_id=1)
session.add(Goggles)

Snowboard = Item(name='Snowboard', catalog_id=5, user_id=1)
session.add(Snowboard)

Twoshinguards = Item(name='Two Shinguards', catalog_id=1, user_id=1)
session.add(Twoshinguards)

Shinguards = Item(name='Shinguards', catalog_id=1, user_id=1)
session.add(Shinguards)

Frisbee2 = Item(name='Frisbee', catalog_id=4, user_id=1)
session.add(Frisbee2)

Bat = Item(name='Bat', catalog_id=2, user_id=1)
session.add(Bat)

Jersey = Item(name='Jersey', catalog_id=1, user_id=1)
session.add(Jersey)

Soccercleats = Item(name='Soccer Cleats', catalog_id=1, user_id=1)
session.add(Soccercleats)

session.commit()

session.close()