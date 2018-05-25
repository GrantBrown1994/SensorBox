import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

user = "root"
host = "35.196.125.44"
port = 3306
dbName = "readings"
instanceConnectionName = "balthazar-168204:us-east1:sensbox"

engine = create_engine('sqlite:///%s' % 'db/db.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

engineCombined = create_engine('sqlite:///%s' % 'db/db.db')
SessionCombined = sessionmaker(bind=engineCombined)
BaseCombined = declarative_base()

engineRemote = create_engine('mysql+mysqldb://%s@%s:%s/%s?unix_socket=/cloudsql/%s' % (user, host, port, dbName, instanceConnectionName))
SessionRemote = sessionmaker(bind=engineRemote)
BaseRemote = declarative_base()

