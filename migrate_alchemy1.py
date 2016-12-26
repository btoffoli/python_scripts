from sqlalchemy import *
from migrate import *

engine = create_engine('postgresql://geocontrol:geo007@localhost:25433/teste1', pool_size=20, max_overflow=0)
#engine = migrate_engine('postgresql://geocontrol:geo007@localhost:25433/teste1')
metadata = MetaData(bind=engine)

mytable = Table('mytable', metadata,
                Column('id', Integer, primary_key=True),   # override reflected 'id' to have primary key
                Column('mydata', Unicode(50)),    # override reflected 'mydata' to be Unicode
                autoload=True)

mytable.create()

#metadata.create_all(engine)