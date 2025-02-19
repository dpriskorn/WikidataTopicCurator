FROM python:3.13.2-alpine3.21

LABEL maintainer="Nizo Priskorn <nizo.priskorn@gmail.com>"

ENV DOCKER=true

WORKDIR /app

COPY pyproject.toml .

# why was there a specific poetry version here?
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false

COPY pyproject.toml .

# Don't install dev dependencies
RUN poetry install --no-interaction --no-ansi --without=dev

COPY . ./
RUN cp config_example.py config.py

# configure the container to run in an executed manner (debug only)
# ENTRYPOINT [ "python" ]
#
# CMD ["app.py" ]

# Run in production using gunicorn and threaded using 20 workers
# We bind via port, not socket
# We increase the to 45s from the default 30 because
# getting data from SPARQL and for labels is quite slow
# Also log requests to console (DEBUG)
CMD ["poetry", "run", "gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120", "--access-logfile", "-"]