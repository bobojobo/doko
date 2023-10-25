#!/usr/bin/env just --justfile

set dotenv-load

default:
  just --list

db-up:
  docker-compose -f docker-compose.yaml up -d --wait db

#db-migrate:
#  cat test_integration/params.sql | docker exec -i db psql -U postgres -w -d phydb

db-shell:
  docker exec -it db psql -U postgres -w doko

db-down:
  docker-compose -f docker-compose.yaml down

api-up:
  uvicorn doko.main:app --reload

docker-api-build:
  docker build -t api .

docker-api-run:
  docker run -d --name api -p 8081:8081 api
