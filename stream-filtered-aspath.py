import asyncio
import websockets
import json

async def listen():
    uri = "wss://ris-live.ripe.net/v1/ws/"
    async with websockets.connect(uri) as websocket:
        # Subscribe to updates for the specific prefix
        message = {
            "type": "ris_subscribe",
            "data": {
                "prefix": "212.48.73.0/24"
            }
        }

        await websocket.send(json.dumps(message))

        # Process incoming messages
        while True:
            response = await websocket.recv()
            data = json.loads(response)

            # Extract only "path" and "withdrawals" if available
            if "data" in data:
                path = data["data"].get("path", [])
                withdrawals = data["data"].get("withdrawals", [])

                print(json.dumps({"path": path, "withdrawals": withdrawals}, indent=2))

# Run WebSocket client
asyncio.run(listen())
