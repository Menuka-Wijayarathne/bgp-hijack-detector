import asyncio
import websockets
import json

# Expected originating ASN
EXPECTED_ORIGIN_ASN = 20773
PREFIX_TO_MONITOR = "212.48.73.0/24"

async def listen():
    uri = "wss://ris-live.ripe.net/v1/ws/"
    async with websockets.connect(uri) as websocket:
        # Subscribe to updates for the specific prefix
        message = {
            "type": "ris_subscribe",
            "data": {
                "prefix": PREFIX_TO_MONITOR
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

                # Ensure we have a valid AS path
                if path:
                    origin_asn = path[-1]  # The last ASN in the path is the origin

                    # Check if the origin ASN is not the expected one
                    if origin_asn != EXPECTED_ORIGIN_ASN:
                        print("🚨 BGP HIJACK ALERT! 🚨")
                        print(f"Expected origin ASN: {EXPECTED_ORIGIN_ASN}, but got: {origin_asn}")
                        print(json.dumps({"path": path, "withdrawals": withdrawals}, indent=2))

# Run WebSocket client
asyncio.run(listen())
