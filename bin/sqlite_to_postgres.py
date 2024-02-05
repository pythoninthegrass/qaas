#!/usr/bin/env python

import platform
import sqlite3
import sys
from decouple import config
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# top-level directory
tld = Path(__file__).resolve().parent.parent

# sqlite data
if len(sys.argv) > 1 and sys.argv[1]:
    sqlite_db = Path(sys.argv[1]).resolve()
else:
    sqlite_db = Path(f"{tld}/db.sqlite").resolve()

# read sqlite data
with sqlite3.connect(sqlite_db) as sqlite_conn:
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT * FROM quotes")
    sqlite_data = sqlite_cursor.fetchall()

# postgres schema
Base = declarative_base()


class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True)
    quote = Column(String, nullable=False)
    author = Column(String, nullable=False)


# postgres connection
db_name = config("POSTGRES_DB", default="quotes")
db_host = config("POSTGRES_HOST", default="localhost")
db_user = config("POSTGRES_USER")
db_pass = config("POSTGRES_PASSWORD")
db_port = config("POSTGRES_PORT",
                  default=5432,
                  cast=int)

# override db_host on darwin
if platform.system() == "Darwin":
    db_host = "localhost"

uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_engine(uri, echo=False)

# create quotes table
Base.metadata.create_all(engine)

# iterate over sqlite data (index, quote, author)
quote_values = [(quote[0], quote[1], quote[2]) for quote in sqlite_data]

# create session
sesh = sessionmaker(bind=engine)

# overwrite quotes table w/sqlite data
with sesh() as session:
    quote_objects = [Quote(id=quote[0], quote=quote[1], author=quote[2]) for quote in quote_values]
    session.bulk_save_objects(quote_objects)
    session.commit()
