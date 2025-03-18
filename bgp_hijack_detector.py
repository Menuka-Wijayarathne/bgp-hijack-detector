import asyncio
import websockets
import json
import yaml
import logging
import requests
import smtplib
import uuid
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(filename="bgp_hijacks.log", level=logging.INFO, format="%(asctime)s - %(message)s")


as_path_log = "bgp_as_paths.log"
processed_log = "bgp_processed.log"

message_queue = asyncio.Queue(maxsize=10000)

def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["prefixes"], config["betterstack_webhook"], config["email_settings"]


def write_to_log(file, prefix, as_path):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    with open(file, "a") as f:
        f.write(f"{timestamp} | Prefix: {prefix} | AS Path: {as_path}\n")

async def send_email_alert(prefix, expected_asn, origin_asn, as_path, email_settings):
    if not email_settings.get("enabled", False):
        return

    sender_email = email_settings["sender_email"]
    recipient_emails = email_settings["recipient_email"]
    smtp_server = email_settings["smtp_server"]
    smtp_port = email_settings["smtp_port"]

    subject = f"🚨 BGP Hijack Alert: {prefix}"
    body = f"""
    **BGP Hijack Detected!**
    - **Prefix:** {prefix}
    - **Expected ASN:** {expected_asn}
    - **Hijacked ASN:** {origin_asn}
    - **AS Path:** {as_path}

    Immediate action required!
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipient_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.set_debuglevel(1)

          
            if email_settings.get("use_authentication", False):
                server.starttls()
                smtp_user = email_settings.get("smtp_username", None)
                smtp_password = email_settings.get("smtp_password", None)
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)

            server.sendmail(sender_email, recipient_emails, msg.as_string())
        
        logging.info(f"Email alert sent for hijack on {prefix}")

    except smtplib.SMTPException as e:
        logging.warning(f" Email alert failed: {e}")


def send_alerts(alert_id, prefix, expected_asn, origin_asn, path, webhook_url, email_settings):
    alert_message = f"🚨 BGP HIJACK ALERT! Prefix: {prefix} Expected ASN: {expected_asn}, but got: {origin_asn}"
    print("\n" + "=" * 60)
    print(alert_message)
    print(f"🔍 AS Path: {path}")
    print("=" * 60 + "\n")
    logging.warning(alert_message)

    if webhook_url:
        payload = {
            "alert_id": alert_id,
            "message": alert_message,
            "prefix": prefix,
            "expected_asn": expected_asn,
            "hijacked_asn": origin_asn,
            "path": path,
            "severity": "high",
            "source": "BGP Hijack Detector"
        }
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            logging.info(f" Alert sent to Better Stack for prefix {prefix}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Failed to send alert: {e}")

    send_email_alert(prefix, expected_asn, origin_asn, path, email_settings)

async def listen(prefixes):
    """ Listen to real-time BGP updates for all prefixes using a single WebSocket connection. """
    uri = "wss://ris-live.ripe.net/v1/ws/"
    
    try:
        async with websockets.connect(uri, ping_interval=30, ping_timeout=10) as websocket:
            # Subscribe to all prefixes in a single WebSocket session
            message = {
                "type": "ris_subscribe",
                "data": {"prefixes": list(prefixes.keys())}
            }
            await websocket.send(json.dumps(message))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)

                if "data" in data and "announcements" in data["data"]:
                    for announcement in data["data"]["announcements"]:  # Iterate through announcements
                        for prefix in announcement["prefixes"]:  # Iterate through all prefixes
                            if prefix in prefixes:  # Check if prefix is in config.yaml
                                as_path = data["data"].get("path", [])

                                print(f"📡 Prefix: {prefix}, AS Path: {as_path}")
                                write_to_log(as_path_log, prefix, as_path)

                                if message_queue.full():
                                    logging.warning("⚠️ Queue is full! Dropping oldest messages.")
                                    await message_queue.get()

                                await message_queue.put((prefix, prefixes[prefix], as_path))

    except websockets.exceptions.ConnectionClosedError as e:
        logging.warning(f"WebSocket disconnected: {e}. Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
        await listen(prefixes)

    except Exception as e:
        logging.warning(f" Unexpected error in listen(): {e}")
        await asyncio.sleep(5)
        await listen(prefixes)

async def process_messages(webhook_url, email_settings):
    while True:
        prefix, expected_asn, as_path = await message_queue.get()
        print(f" Processing message. Queue size before: {message_queue.qsize()}")

        if as_path:
            origin_asn = as_path[-1]
            

            if origin_asn != expected_asn:
                alert_id = f"{prefix.replace('/', '_')}_{origin_asn}_{uuid.uuid4().hex[:6]}"
                write_to_log(processed_log, prefix, as_path)
                send_alerts(alert_id, prefix, expected_asn, origin_asn, as_path, webhook_url, email_settings)

        message_queue.task_done()
        print(f"Processed message. Queue size after: {message_queue.qsize()}")


async def monitor_queue():
    while True:
        logging.info(f" Queue Size: {message_queue.qsize()}")
        print(f"Queue Size: {message_queue.qsize()}")
        await asyncio.sleep(10)


async def main():
    prefixes, webhook_url, email_settings = load_config()

    listener_task = asyncio.create_task(listen(prefixes))  # Single listener for all prefixes
    processor_task = asyncio.create_task(process_messages(webhook_url, email_settings))
    monitor_task = asyncio.create_task(monitor_queue())

    await asyncio.gather(listener_task, processor_task, monitor_task)

if __name__ == "__main__":
    asyncio.run(main())
