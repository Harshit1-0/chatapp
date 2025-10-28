from fastapi import WebSocket , FastAPI , WebSocketDisconnect
from typing import List
app = FastAPI()
from fastapi.responses import FileResponse


class ConnectionManager :
    def __init__(self) :
        self.active_connection = {}
    async def connect(self , websocket : WebSocket , username) :
        await websocket.accept()
        self.active_connection[username] = websocket
    
    
    def disconnect(self , websocket : WebSocket , username) :
        if username in self.active_connection:
            del self.active_connection[username]
    

    async def broadcast(self , message) :
        for connection in self.active_connection.values() :
            await connection.send_text(message)

    
    async def send_private_message(self , sender , reciever , message) :
        if reciever in self.active_connection : 
            await self.active_connection[sender].send_text(f'private messsage to  {reciever} : {message}')
            await self.active_connection[reciever].send_text(f'private message by {sender} : {message}')
        else :
            print('There is no user like this')

manager = ConnectionManager()



@app.get('/')
async def main():
    return FileResponse('index.html')
@app.websocket('/ws')
async def websocket_endpoint(username : str , websocket :WebSocket) :
    await manager.connect(websocket , username)
    await manager.broadcast(f'{username} joined the chat')
    
    
    try : 
        while True :
            data = await websocket.receive_text()
            if(data.startswith('/pm')):
                _, reciever , message  = data.split(' ' , 2)
                print(reciever , message)
                await manager.send_private_message(username , reciever , message )
            else :

                await manager.broadcast(f'{username} : {data}')
    
    
    
    except WebSocketDisconnect :
        manager.disconnect(websocket , username)
        await manager.broadcast(f'{username} left the chat') 
