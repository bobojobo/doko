#!/usr/bin/env just --justfile

set dotenv-load

default:
  just --list

db-up:
  docker-compose -f docker-compose.yaml up -d --wait db

db-shell:
  docker exec -it db psql -U postgres -w doko

db-down:
  docker-compose -f docker-compose.yaml down

api-up:
  uvicorn doko.main:app --reload

full-run:
  docker compose up
