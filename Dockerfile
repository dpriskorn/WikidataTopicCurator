#FROM python:3.11-slim
FROM python:3.11

LABEL maintainer="Dennis Priskorn <priskorn@riseup.net>"

ENV DOCKER=true

WORKDIR /app

COPY pyproject.toml .

# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir poetry && \
#     poetry install

RUN pip install --no-cache-dir poetry==1.7.1 && poetry config virtualenvs.create false

COPY pyproject.toml .

# Don't install dev dependencies
RUN poetry install --no-interaction --no-ansi --without=dev

COPY . ./

CMD ["whereis", "gunicorn"]
#CMD ["poetry run gunicorn -w 30 --bind unix:/tmp/gunicorn_ipc.sock wsgi:app --timeout 60"]