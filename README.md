# Co2 Calculator API

## Local Development

## Using Docker

To build the application container, use

```bash
docker build . -t co2-calculator-api
```

You can then start the app and database containers using:

```bash
docker compose up --detach
```

Or just start the database using:

```bash
docker-compose up --detach database
```

### Using Locally installed Python and Postgres

The project runs with *Python 3.10.1*.

Install packages:

```bash
pip install -r requirements.txt
```

Run the local development server:

```bash
uvicorn app.main:app --reload --reload-dir app --log-level debug
```

## Deployment

The API is hosted on Heroku at [co2-calculator-api.herokuapp.com](https://co2-calculator-api.herokuapp.com/)

```api
git push https://git.heroku.com/co2-calculator-api.git main
```
