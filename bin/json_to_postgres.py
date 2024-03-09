#!/usr/bin/env python

import json
import psycopg2
import sys
from decouple import config, UndefinedValueError
from pathlib import Path
from psycopg2 import sql

# read json data
if len(sys.argv) > 1 and sys.argv[1]:
    raw_db = Path(sys.argv[1]).resolve()
else:
    raw_db = Path("../db.json")

with open(raw_db) as f:
    data = json.load(f)

# iterate over json data (index, quote, author)
quotes = [(key, value['quote'],
           value['author']) for key, value in data['_default'].items()]

# postgres connection
try:
    db_uri = config("DATABASE_URL")
except UndefinedValueError:
    db_name = config("POSTGRES_DB")
    db_host = config("POSTGRES_HOST")
    db_user = config("POSTGRES_USER")
    db_pass = config("POSTGRES_PASSWORD")
    db_port = config("POSTGRES_PORT",
                    default=5432,
                    cast=int)
    db_uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

uri = db_uri

# connect to your postgres db
conn = psycopg2.connect(uri)

# open a cursor to perform database operations
cur = conn.cursor()

# ! drop table if it already exists (qa)
cur.execute("DROP TABLE IF EXISTS quotes")

# create the table
cur.execute(
    "CREATE TABLE quotes (id INTEGER PRIMARY KEY, quote TEXT, author TEXT)"
)

# insert the data
values = ','.join(cur.mogrify("(%s, %s, %s)", quote).decode("utf-8") for quote in quotes)
insert = f"INSERT INTO quotes (id, quote, author) VALUES {values}"
cur.execute(insert)

# commit changes and close
conn.commit()
cur.close()
conn.close()
