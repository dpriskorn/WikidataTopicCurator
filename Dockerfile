FROM python:3.11-slim
#FROM python:3.11

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

#CMD ["whereis", "gunicorn"]
#CMD ["whereis", "poetry"]
#CMD ["poetry", "--version"]
#CMD ["gunicorn", "--version"]
#CMD ["poetry run -vvv gunicorn"]
#CMD ["poetry run gunicorn -w 30 --bind unix:/tmp/gunicorn_ipc.sock wsgi:app --timeout 60"]

# configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]
#
# CMD ["app.py" ]
# Run in production using gunicorn and threaded using 20 workers
#CMD ["poetry", "run", "gunicorn", "-vvv","-w", "20", "-b", "0.0.0.0:5000", "app:app"]
CMD ["poetry", "run", "gunicorn", "-w", "20", "-b", "0.0.0.0:5000", "app:app"]