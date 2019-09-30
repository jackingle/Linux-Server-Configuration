from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Spell, School, User

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

q =  session.query(School).all()

for School in q:
    print (School.name)

items = session.query(Spell).all()
for Spell in items:
        print (Spell.id, Spell.name)

usr = session.query(User).all()

for User in usr:
    print(User.id)
