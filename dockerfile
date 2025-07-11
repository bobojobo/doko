FROM python:3.11

WORKDIR /doko

# todo: make a nicer dockerfile
COPY ./pyproject.toml /doko/pyproject.toml
COPY ./doko /doko/doko

RUN pip install --no-cache-dir --upgrade -e /doko[dev]

CMD ["uvicorn", "doko.main:app", "--host", "0.0.0.0", "--port", "8081"]
