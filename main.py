from fastapi import FastAPI, Request
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from fastapi.templating import Jinja2Templates


# These default settings get overridden by environment variables. @see https://fastapi.tiangolo.com/advanced/settings/
class Settings(BaseSettings):
    websocket_endpoint: str = "ws://localhost:8000/ws"


settings = Settings()
app = FastAPI()
templates = Jinja2Templates("templates")


@app.get("/")
def read_root():
    return {"websocket_endpoint": settings.websocket_endpoint}


@app.get("/chat")
async def get(request: Request):
    return templates.TemplateResponse("chat.jinja", {"request": request, "websocket_endpoint": settings.websocket_endpoint})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
