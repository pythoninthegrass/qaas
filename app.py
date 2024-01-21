#!/usr/bin/env python

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get('/hello')
def hello():
    return 'Hello, World!'


@app.get('/')
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
