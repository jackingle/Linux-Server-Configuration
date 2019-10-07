from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, School, Spell, User
"""
This creates an engine attached to the database.
"""
engine = create_engine('sqlite:///spell.db')
"""
Bind the engine to the metadata of the Base class so that the declaratives
can be accessed through a DBSession instance.
"""
Base.metadata.bind = engine
"""
Create an instance of the instance that can handle sessions.
"""
DBSession = sessionmaker(bind=engine)
"""
A DBSession() instance establishes all conversations with the database
and represents a "staging zone" for all the objects loaded into the
database session object. Any change made against the objects in the
session won't be persisted into the database until you call
session.commit(). If you're not happy about the changes, you can
revert all of them back to the last commit by calling
session.rollback().
"""
session = DBSession()
"""
Populate the database with beginning information.  These instances are passed
into the session and then committed.
"""
Item1 = School(
                name="Evocation",
                id=1,
                user_id=1,)
session.add(Item1)
session.commit()

Item2 = School(
                name="Abjuration",
                id=1, user_id=1,
                description="spells of protection, blocking, and banishing.")
session.add(Item2)
session.commit()

Spell1 = Spell(
                name="Fireball",
                description="Ball of flame.",
                school_id="Evocation")
session.add(Spell1)
session.commit()

Spell2 = Spell(
                name="Alarm",
                school_id="Abjuration",
                description="You set an alarm against unwanted intrusion.",
                user_id=1)
session.add(Spell2)
session.commit()

User1 = User(
            id=1,
            name="placeholder",
            email="jack@placeholder.com",
            picture="something.jpg")
session.add(User1)
session.commit()
"""
Provide console confirmation that the items were succesfully added.
"""
print ("Added data to the database successfully!")
