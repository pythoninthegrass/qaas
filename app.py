#!/usr/bin/env python

import sqlite3
from fastapi import FastAPI, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# TODO: fix optional name parameter
@app.get('/hello/{name}')
def hello(name: Optional[str] = None) -> JSONResponse:
    if name:
        message = f"Hello, {name}!"
    else:
        message = f"Hello, World!"
    return JSONResponse(content={"hello": message})


# TODO: improve sql performance
@app.get('/all')
def get_quotes(request: Request) -> JSONResponse:
    db = sqlite3.connect("db.sqlite")
    c = db.cursor()
    c.execute("SELECT * FROM quotes")
    quotes = c.fetchall()
    db.close()
    return JSONResponse(content={"quotes": quotes})


@app.get('/quotes/{limit}')
def get_quotes_by_limit(request: Request, limit: int) -> JSONResponse:
    db = sqlite3.connect("db.sqlite")
    c = db.cursor()
    c.execute(f"SELECT * FROM quotes ORDER BY RANDOM() LIMIT {limit}")
    quotes = [{"id": id,
               "quote": quote,
               "author": author} for id, quote, author in c.fetchall()]
    db.close()
    return JSONResponse(content={"quotes": quotes})
