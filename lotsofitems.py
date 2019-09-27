from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Item, Base, Equipment, User

engine = create_engine('sqlite:///items.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



#Menu for UrbanBurger
Item1 = Item(name = "Pation", id = 201, user_id = 1)

session.add(Item1)
session.commit()


Equipment1 = Equipment(name = "Sword", description = "Your basic sword.", type = "Weapon", user_id = 1)

session.add(Equipment1)
session.commit()

User1 = User(id = 1, name = "Jack", email = "jack@jack.com", picture="something.jpg")

session.add(User1)
session.commit()

print ("added items!")
