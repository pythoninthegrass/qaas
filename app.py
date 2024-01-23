#!/usr/bin/env python

from decouple import config
from fastapi import FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from random import randint
from sqlalchemy import bindparam, create_engine, text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Optional

# postgres schema
Base = declarative_base()

class Quote(Base):
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True)
    quote = Column(String, nullable=False)
    author = Column(String, nullable=False)

# postgres connection
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

# fastapi instantiation
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
    """Health check endpoint"""
    return JSONResponse(content={"status": "ok"})


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})


# TODO: fix optional name parameter
@app.get('/hello/{name}')
def hello(name: Optional[str] = None) -> JSONResponse:
    """Hello, World!"""
    if name:
        message = f"Hello, {name}!"
    else:
        message = "Hello, World!"
    return JSONResponse(content={"hello": message})


# TODO: improve sql performance
@app.get('/all')
def get_quotes(request: Request) -> JSONResponse:
    """Get all quotes"""
    with Session(conn) as session:
        quotes = session.query(Quote).all()
        result = [{"id": quote.id, "quote": quote.quote, "author": quote.author} for quote in quotes]
    return JSONResponse(content={"quotes": result})


@app.get('/quotes/{limit}')
def get_quotes_by_limit(request: Request, limit: int) -> JSONResponse:
    """Get quotes by limit"""
    with Session(conn) as session:
        count = session.query(Quote).count()
        if count > 0:
            random_index = randint(0, count - 1)
            quote = session.query(Quote).offset(random_index).limit(limit).first()
            result = [{"id": quote.id, "quote": quote.quote, "author": quote.author}]
        else:
            result = []
    return JSONResponse(content={"quotes": result})
