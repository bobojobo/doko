# ♣️ ♥️ Doko ♠️ ♦️

## Description
A [Doppelkopf](https://en.wikipedia.org/wiki/Doppelkopf) webapp. Just to learn about [lob](https://htmx.org/essays/locality-of-behaviour/)bing everything with the [HAT](https://twitter.com/htmx_org/status/1403389705039736835?lang=en) stack and to fool around with python asyncio:
- Mom, can we have async frontend?
- No, we have async in backeend.
- 🤷

## Stack: 🎩🐍🐘 
* Frontend: 🎩 ([htmx](https://htmx.org/) + [Alpine.js](https://alpinejs.dev/) + [tailwindcss](https://tailwindcss.com/))
* Backend: 🐍 ([Python](https://www.python.org/) + [FastAPI](https://fastapi.tiangolo.com/) + [Jinja](https://jinja.palletsprojects.com/))
* Database: 🐘 ([PostgreSQL](https://www.postgresql.org/))


## Prerequisits
* [Python](https://www.python.org/) (>= 3.11)
* [Docker](https://www.docker.com/)
* [Docker-compose](https://docs.docker.com/compose/)
* [Just](https://github.com/casey/just)


## Run
```bash
just run
```
This will spin up two dockers, one with a postgresql database and one with the rest api. You can reach it at 
http://127.0.0.1:8000


## Develop
```bash
pip install .[dev]
```
Find more helpfull commands here:
```bash
just
```

The `.env` file provides the configuration. It is **not** autoreloaded when running the application!
