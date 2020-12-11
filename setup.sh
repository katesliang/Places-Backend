#!/bin/sh

echo "Building + Running containers"
docker-compose build # --no-cache
docker-compose up -d 

echo "Creating + Seeding DB"
docker-compose exec api python manage.py recreate_db
docker-compose exec api python manage.py seed_db

echo "Linting"
docker-compose exec api flake8 src

echo "Running + Editing using Black"
docker-compose exec api black src 
