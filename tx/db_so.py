'''
Texata 2014 Finals Solution.
StackOverflow data model.

Copyright: Konstantin Tretyakov
License: MIT
'''


from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base


# ------------------------- Data model ---------------------- #
Base = declarative_base()

def _saobject_repr(self):
    s = [self.__class__.__name__, '\n']
    for c in self.__class__.__table__.columns:
        s.extend(['\t', c.name, ': ', str(getattr(self, c.name)), '\n'])
    return ''.join(s)
Base.__repr__ = _saobject_repr

def nvl(x):
    return x if x is not None else ''

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    accepted_answer_id = Column(Integer)
    answer_count = Column(Integer)
    comment_count = Column(Integer)
    creation_date = Column(DateTime)
    favorite_count = Column(Integer)
    last_activity_date = Column(DateTime)
    last_edit_date = Column(DateTime)
    owner_user_id = Column(Integer, ForeignKey('se_user.id'))
    parent_id = Column(Integer)
    post_type_id = Column(Integer)
    score = Column(Integer)
    tags = Column(Unicode(255))
    view_count = Column(Integer)
    title = Column(Unicode)
    body = Column(Unicode)
    
    @property
    def all_text(self):
        return nvl(self.title) + ' ' + nvl(self.body)
        
class PostLink(Base):
    __tablename__ = 'post_link'
    id = Column(Integer, primary_key=True)
    creation_date = Column(DateTime)
    link_type_id = Column(Integer)
    post_id = Column(Integer)
    related_post_id = Column(Integer)

class SeUser(Base):
    __tablename__ = 'se_user'
    id = Column(Integer, primary_key=True)
    about_me = Column(Unicode)
    creation_date = Column(DateTime)
    display_name = Column(Unicode(255))
    down_votes = Column(Integer)
    email_hash = Column(String(255))
    last_access_date = Column(DateTime)
    location = Column(Unicode(255))
    reputation = Column(Integer)
    up_votes = Column(Integer)
    views = Column(Integer)

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    count = Column(Integer)
    excerpt_post_id = Column(Integer)
    tag_name = Column(Unicode(255))
    wiki_post_id = Column(Integer)

# ----------------- DB connection helper ------------ #
DBSession = scoped_session(sessionmaker())
Engine = None

def connect_db(db_url):
    global Engine, DBSession
    Engine = create_engine(db_url)
    DBSession.configure(bind=Engine)
    Base.metadata.bind = Engine

def init_db():
    Base.metadata.drop_all()
    Base.metadata.create_all()
