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

# q =  session.query(School).all()
#
# for School in q:
#     print (School.name, School.id)
#
# items = session.query(Spell).all()
# for Spell in items:
#         print (Spell.school_id, Spell.name, Spell.user_id)

# usr = session.query(User).all()
#
# for User in usr:
#     print(User.id, User.email, User.name)

# spells = session.query(Spell).filter_by(
#     spell_id=Spell.id).all()

# school_id = 1
# schools = session.query(School).filter_by(id=school_id).one()
# for school in schools:
#     print(school.name, school.id)

spells = session.query(Spell).filter_by(school_id="Abjuration").all()

for spell in spells:
     print(spell.id, spell.name, spell.description)

# deleteSpell = session.query(Spell).filter_by(id=1).one()
#
# session.delete(deleteSpell)
# session.commit()

# Spell1 = School(id = 2, name = "Evocation", description = "Spells that manipulate energy or create something from nothing. ", user_id = 1)
#
# session.add(Spell1)
# session.commit()
