#! /usr/bin/env bash

# Let the DB start
python ./app/prestart.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python ./app/initial_data.py
