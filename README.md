BGP Hijack Detection Tool
Real-time BGP monitoring for detecting unauthorized route announcements and potential prefix hijacks.

🚀 Features
✅ Real-time BGP monitoring using the RIS-Live WebSocket feed.
✅ Detect unauthorized prefix announcements and BGP hijacks.
✅ Instant alerts via email and Better Stack Webhooks.
✅ Efficient queue-based processing to handle large-scale BGP updates.
✅ Automatic reconnection mechanism in case of WebSocket disconnects.

🛠 Installation
1️⃣ Clone the Repository

git clone https://github.com/Menuka-Wijayarathne/bgp-hijack-detector.git
cd bgp-hijack-detector

2️⃣ Create and Activate a Virtual Environment (Optional)
python3 -m venv myenv
source myenv/bin/activate  # On macOS/Linux
myenv\Scripts\activate  # On Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

⚙️ Configuration (config.yaml)
Modify config.yaml to customize the prefixes to monitor, email settings, and webhook alerts.
Edit the config.yaml file to specify:

Prefixes to monitor (e.g., 31.170.120.0/21).
Expected ASN for each prefix (e.g., 20738).
Webhook URL for Better Stack alerts.
Email settings (SMTP server, sender, recipients, etc.).

Example config.yaml

prefixes:
  "31.170.120.0/21": 20738
  "46.32.224.0/19": 20738

betterstack_webhook: "https://uptime.betterstack.com/api/v1/incoming-webhook/your-webhook-id"

email_settings:
  enabled: true
  sender_email: "bgp-hijack@yourdomain.com"
  recipient_email:
    - "alert1@yourdomain.com"
    - "alert2@yourdomain.com"
  smtp_server: "10.93.131.42"
  smtp_port: 25
  use_authentication: false

  ▶️ Running the Tool

  To start real-time monitoring:(select correct interpreter path)

  python bgp_hijack_detector.py

if you need to run this as a background process, better to configure a seperate systemd service for this.

This will:

Subscribe to the RIPE RIS Live WebSocket feed.
Monitor and log AS paths for configured prefixes.
Trigger alerts for hijacked prefixes.
Store logs for later analysis.


📁 Log Files
bgp_as_paths.log → Logs all AS paths received.
bgp_processed.log → Logs hijack detections.
bgp_hijacks.log → General application logs.

🔄 Troubleshooting
1️⃣ No Alerts Being Sent?
Check config.yaml to ensure prefixes and ASN values are correctly set.
Verify your SMTP server is reachable (ping your-smtp-server).
Ensure the WebSocket connection is active (check logs for disconnect messages).
2️⃣ Getting WebSocket Disconnects?
The WebSocket may limit connections. Ensure only one instance is running.
If experiencing frequent disconnects, increase the ping_interval in the WebSocket configuration.


👨‍💻 Contributing
We welcome contributions! To contribute:

Fork this repository.
Create a feature branch:

git checkout -b feature-branch
Commit your changes:

git commit -m "Added new feature"
Push to your branch:

git push origin feature-branch
Create a Pull Request (PR) on GitHub.
