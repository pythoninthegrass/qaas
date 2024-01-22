#!/usr/bin/env bash

gunicorn \
	-k uvicorn.workers.UvicornWorker \
	-b 0.0.0.0:8000 \
	--reload \
	--reload-extra-file="templates/index.html" \
	--reload-extra-file="static/styles.css" \
	app:app
