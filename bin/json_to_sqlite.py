#!/usr/bin/env python

import json
import sqlite3
from pathlib import Path

raw_db = Path("../db.json")
db = Path("../db.sqlite")

# ! remove the db if it exists (qa)
if db.exists():
    db.unlink()

if not db.exists():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(
        "CREATE TABLE quotes (id INTEGER PRIMARY KEY, quote TEXT, author TEXT)"
    )
    conn.commit()
    conn.close()

with open(raw_db) as f:
    data = json.load(f)

quotes = set()

quotes = [(key, value['quote'],
           value['author']) for key, value in data['_default'].items()
]

conn = sqlite3.connect(db)
c = conn.cursor()
c.executemany("INSERT INTO quotes VALUES (?, ?, ?)", quotes)
conn.commit()
conn.close()
