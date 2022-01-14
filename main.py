from fastapi import FastAPI, Request
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from fastapi.staticfiles import StaticFiles


# These default settings get overridden by environment variables. @see https://fastapi.tiangolo.com/advanced/settings/
class Settings(BaseSettings):
    websocket_endpoint: str = "ws://localhost:8000/footprint"


settings = Settings()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return {"message": "Hello world!"}


@app.websocket("/footprint")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/footprint/settings")
def read_root():
    return {"websocket_endpoint": settings.websocket_endpoint}
