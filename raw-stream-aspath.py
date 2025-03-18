import asyncio
import websockets
import json

async def listen():
    uri = "wss://ris-live.ripe.net/v1/ws/"
    async with websockets.connect(uri) as websocket:
        # Subscribe to Firehose for ALL BGP updates
        message = {
            "type": "ris_subscribe",
            "data": {
                "prefix": "212.48.73.0/24"
            }
        }

        await websocket.send(json.dumps(message))

        # Print incoming messages
        while True:
            response = await websocket.recv()
            print(response)

# Run WebSocket client
asyncio.run(listen())