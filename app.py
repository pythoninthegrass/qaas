#!/usr/bin/env python

from decouple import config
from fastapi import FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Optional

db_name = config("POSTGRES_DB")
db_host = config("POSTGRES_HOST")
db_user = config("POSTGRES_USER")
db_pass = config("POSTGRES_PASSWORD")
db_port = config("POSTGRES_PORT",
                  default=5432,
                  cast=int)

uri = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
conn = create_engine(uri, echo=False)
sesh = sessionmaker(bind=conn)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/healthz')
def healthz() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# TODO: fix optional name parameter
@app.get('/hello/{name}')
def hello(name: Optional[str] = None) -> JSONResponse:
    if name:
        message = f"Hello, {name}!"
    else:
        message = "Hello, World!"
    return JSONResponse(content={"hello": message})


# TODO: improve sql performance
@app.get('/all')
def get_quotes(request: Request) -> JSONResponse:
    session = sesh()
    quotes = session.execute("SELECT * FROM quotes").fetchall()
    session.close()
    return JSONResponse(content={"quotes": quotes})


@app.get('/quotes/{limit}')
def get_quotes_by_limit(request: Request, limit: int) -> JSONResponse:
    session = sesh()
    quotes = session.execute(text(f"SELECT * FROM quotes ORDER BY RANDOM() LIMIT {limit}")).fetchall()
    session.close()
    quotes = [{"id": id,
               "quote": quote,
               "author": author} for id, quote, author in quotes]
    return JSONResponse(content={"quotes": quotes})
