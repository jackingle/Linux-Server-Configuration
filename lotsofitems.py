from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, School, Spell, User

engine = create_engine('sqlite:///spell.db')
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
# Item1 = School(name = "Conjuration", id = 1, user_id = 1,)
# # Item1 = School(name = "Abjuration", id = 1, user_id = 1, description = "spells of protection, blocking, and banishing.")
# #
# session.add(Item1)
# session.commit()
#
# Spell1 = School(id = 2, name = "Evocation", description = "Spells that manipulate energy or create something from nothing. ", user_id = 1)
#
# session.add(Spell1)
# session.commit()
# #
# Spell1 = Spell(name = "Alarm", school_id = "Abjuration", description = "You set an alarm against unwanted intrusion. Choose a door, a window, or an area within range that is no larger than a 20-foot cube. Until the spell ends, an alarm alerts you whenever a Tiny or larger creature touches or enters the warded area. When you cast the spell, you can designate creatures that won't set off the alarm. You also choose whether the alarm is mental or audible.", user_id = 1)
#
# session.add(Spell1)
# session.commit()
#
# User1 = User(id = 1, name = "Jack", email = "jack@jack.com", picture="something.jpg")
#
# session.add(User1)
# session.commit()
#
# Usr2 = User(id = 243, name = "Jack", email = "jaxon.chillforce@gmail.com")
#
# session.add(Usr2)
# session.commit()

print ("added items!")
