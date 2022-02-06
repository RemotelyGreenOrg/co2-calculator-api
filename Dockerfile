FROM python:3.10.1

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /app/app/
COPY ./static /app/static/

WORKDIR /app/

EXPOSE 8000

CMD [ "uvicorn", "app.main:app", "--reload", "--reload-dir", "app", "--log-level", "info", "--host", "0.0.0.0" ]
