import asyncio
import websockets
import json

async def listen():
    uri = "wss://ris-live.ripe.net/v1/ws/"
    async with websockets.connect(uri) as websocket:
        # Subscribe to all BGP UPDATE messages for the prefix
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

            # Ensure message is a BGP UPDATE type
            if data["data"]["type"] == "UPDATE":
                withdrawals = data["data"].get("withdrawals", [])

                # Check if "212.48.73.0/24" is in withdrawals
                if "212.48.73.0/24" in withdrawals:
                    print("🚨 ALERT: Prefix 212.48.73.0/24 has been withdrawn! 🚨")
                    print(json.dumps({"withdrawals": withdrawals}, indent=2))

# Run WebSocket client
asyncio.run(listen())
