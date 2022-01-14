from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocket

# MODULES:
from importlib import import_module
moduleNames = ['template_module', 'another_module']
import_module('src.template_module','template_module')
import_module('src.another_module')

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World!"}


html = """
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
            var ws = new WebSocket("wss://co2-calculator-api.herokuapp.com/ws");
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
"""

@app.get("/chat")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.get("/modules")
async def get():
    interfaces = []
    # for module in (__import__("src."+m) for m in moduleNames):
    #     print(module)
    interfaces.append(template_module.interface())
    interfaces.append(another_module.interface())
    module_json = { 'modules': interfaces}
    return module_json