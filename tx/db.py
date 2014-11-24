'''
Texata 2014 Finals Solution.
Data model & import script.

Copyright: Konstantin Tretyakov
License: MIT
'''

from dateutil import parser
import glob
import logging
import os
import warnings

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ------------------------- Data model ---------------------- #
Base = declarative_base()

def _saobject_repr(self):
    '''
    This is the generic __repr__ we'll add to all SQLAlchemy models.
    It just pretty-prints the field names and values.
    '''
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
    timestamp = Column(DateTime)
    title = Column(Unicode)
    body = Column(Unicode)
    url = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    reply_count = Column(Integer)
    avg_rating = Column(Integer)
    view_count = Column(Integer)
    vote_count = Column(Integer)
    share_count = Column(Integer)
    parse_problems = Column(Boolean)
    replies = relationship('Reply', backref='post', order_by='Reply.timestamp')

    @property
    def all_text(self):
        return nvl(self.title) + ' ' + nvl(self.body)

class Reply(Base):
    __tablename__ = 'reply'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    body = Column(Unicode)
    user_id = Column(Integer, ForeignKey('user.id'))
    post_id = Column(Integer, ForeignKey('post.id'))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    posts = relationship('Post', backref='user', order_by='Post.timestamp')
    replies = relationship('Reply', backref='user', order_by='Reply.timestamp')    


# ------------------------- Data import ---------------------- #

import traceback
def parse_post(fname, user_cache):
    '''
    Parse a given file into a set of Post, Reply and User objects.
    User objects are reused from the given dict.
    Returns the post object or None on failure.
    '''
    
    def parse_reply(fin, type='Reply:'):
        '''Reads the next two lines from the file and parses them into a (user, date, text) tuple.'''
        header = unicode(fin.readline(), 'utf-8')
        body = unicode(fin.readline(), 'utf-8')
        assert header.startswith(type)
        uname, date = header[len(type)+1:].split(u' / ')
        user_cache.setdefault(uname, User(name=uname))
        date = parser.parse(date)
        return (user_cache[uname], date, body)  # XXX: Description objects may end with "xxx vote(s)" text which should be stripped away
    
    def parse_statistics(fin):
        ln = fin.readline().split()
        assert ln[0] == 'Statistics:'
        assert ln[1] == 'Replies:'
        replies = int(ln[2])
        assert ln[3] == '\xc2\xa0'
        assert ln[4] == 'Avg.'
        if ln[6] == 'Views:':
            avg_rating = None
            ln = ln[7:]
        else:
            avg_rating = float(ln[6])
            ln = ln[8:]
        views = int(ln[0])
        assert ln[1] == '\xc2\xa0'
        assert ln[2] == 'Votes:'
        votes = int(ln[3])
        assert ln[4] == 'Shares:'
        shares = int(ln[5])
        assert fin.readline().strip() == ''
        return replies, avg_rating, views, votes, shares
        
    try:
        p = Post(id=int(os.path.basename(fname).split('_')[0]), parse_problems=False)
        with open(fname) as fin:
            firstline = fin.readline()
            if firstline.strip() == '':
                firstline = fin.readline()
            assert firstline.strip() == 'Title:'
            p.title = unicode(fin.readline().strip(), 'utf-8')
            assert fin.readline().strip() == ''
            assert fin.readline().strip() == 'URL:'
            p.url = fin.readline().strip()
            assert fin.readline().strip() == ''
            p.reply_count, p.avg_rating, p.view_count, p.vote_count, p.share_count = parse_statistics(fin)
            p.user, p.timestamp, p.body = parse_reply(fin, 'Description:')
            ix = p.body.find('I have this problem too')
            if ix == -1:
                p.parse_problems = True
                ix = p.body.find('Please rate helpful posts')
                if ix == -1:
                    ix = len(p.body)+1
            p.body = p.body[0:(ix-1)]
            while fin.readline() != '':
                u, timestamp, body = parse_reply(fin)
                r = Reply(user=u, timestamp=timestamp, body=body, post=p)
        return p
    except Exception, e:
        traceback.print_exc()
        log.error("Error parsing file %s", fname)
        log.error(e)
        return None

def import_dir(data_dir, session, max_files=-1):
    '''
    Given a directory with posts, loads them into the given database session.
    '''
    files = sorted(glob.glob(os.path.join(data_dir, '*.txt')))
    user_cache = dict()  # name -> User
    s = Session()
    ctr = 0
    for f in files:
        if ctr == max_files:
            break
        p = parse_post(f, user_cache)
        if p is None:
            warnings.warn("Failed to import %s" % f)
        else:
            s.add(p)
        if p is not None:
            s.add(p)
        ctr += 1
        if ctr % 10000 == 0:
            log.debug("%d files imported..." % ctr)
    s.commit()

# ----------------- DB connection helpers ------------ #
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
