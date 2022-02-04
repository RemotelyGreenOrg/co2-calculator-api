web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-5000}
release: alembic upgrade head
