from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocket
from pydantic import BaseSettings
from jinja2 import Template


class Settings(BaseSettings):
    websocket_endpoint: str = "ws://localhost:8000/ws"


settings = Settings()
app = FastAPI()


@app.get("/")
def read_root():
    return {"websocket_endpoint": settings.websocket_endpoint}


html = Template("""
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("{{websocket_endpoint}}");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
""")


@app.get("/chat")
async def get():
    return HTMLResponse(html.render(websocket_endpoint=settings.websocket_endpoint))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
