# Co2 Calculator API

## Local Development

The project runs with *Python 3.10.1*.

Install packages:

```bash
pip install -r requirements.txt
```

Run the local development server:

```bash
uvicorn main:app --reload
```

## Deployment

The API is hosted on Heroku at [co2-calculator-api.herokuapp.com](https://co2-calculator-api.herokuapp.com/)

```api
git push https://git.heroku.com/co2-calculator-api.git main
```
