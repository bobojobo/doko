FROM python:3.11

WORKDIR /code

# todo docker ignore? or are we fine here?
# todo: make a nicer dockerfile
COPY ./pyproject.toml /code/pyproject.toml
COPY ./doko /code/doko

RUN pip install --no-cache-dir --upgrade /code

CMD ["uvicorn", "doko.main:app", "--host", "0.0.0.0", "--port", "8081"]
