import warnings
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import expression
from sqlalchemy import create_engine
from sqlalchemy import ThreadLocalMetaData
import sqlalchemy.databases as sd 
from sqlalchemy import func
from sqlalchemy import schema
from elixir import *
from sqlalchemy import exc as sa_exc

warnings.simplefilter("ignore", category=sa_exc.SAWarning)
b_engine = create_engine("postgresql://jobreporter:jobreporter@128.208.190.71/joblog",
        echo=False, convert_unicode=False, poolclass=NullPool)
b_session = application_session = scoped_session(sessionmaker(autoflush=True,
     bind=b_engine))
b_metadata = ThreadLocalMetaData()
b_metadata.bind = b_engine

class CatalogEventLog (Entity):
  using_options(tablename='eventlog', metadata=b_metadata, session=b_session)
  jobid = Field(Integer, index=True)
  owner = Field(UnicodeText)
  pkey = Field(UnicodeText)
  pvalue = Field(UnicodeText)
  time = Field(DateTime(timezone=True))
  taskNumber = Field(Integer)
  ip = Field(sd.postgres.PGInet)
  description = Field(UnicodeText)
  def __repr__(self):
    return '<Log Event (%s,%s) at %s>' % (self.pkey, self.pvalue, self.time)

class JobStateLog (Entity):
  using_options(tablename='statelog', metadata=b_metadata, session=b_session)
  jobid = Field(Integer, index=True)
  owner = Field(Text)
  pkey = Field(Text)
  pvalue = Field(Text)
  time = Field(DateTime(timezone=True))
  def __repr__(self):
    return '<Log state (%s,%s) at %s>' % (self.pkey, self.pvalue, self.time)
