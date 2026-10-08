import json
import os
import requests
import ovh

# ==========================================
# CONFIGURATION
# ==========================================

# Add your Discord Webhook URLs here
DISCORD_WEBHOOKS = [
    "https://discord.com/api/webhooks/154....",    #1
    "https://discord.com/api/webhooks/14605...."     #2
]

# OVH API Credentials
APPLICATION_KEY = "xxxxxxxxxxxxxxxx"
APPLICATION_SECRET = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
CONSUMER_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# IP Addresses to monitor
TARGET_IPS = [
    "xxx.xxx.xxx.xxx",
    "xxx.xxx.xxx.xxx"
]

# Local file to save state (prevents spamming notifications every minute)
STATUS_FILE = "/root/ddos_status.json"

# ==========================================
# SCRIPT LOGIC
# ==========================================

client = ovh.Client(
    endpoint='ovh-eu',
    application_key=APPLICATION_KEY,
    application_secret=APPLICATION_SECRET,
    consumer_key=CONSUMER_KEY,
)

def load_status():
    """Loads previous status from JSON file."""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_status(status):
    """Saves current status to JSON file."""
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f)

def send_discord_alert(title, description, color, ip):
    """Sends Embed message to all Discord Webhooks in the list."""
    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": f"OVH Anti-DDoS Protection System | IP: {ip}"}
        }]
    }
    
    for webhook_url in DISCORD_WEBHOOKS:
        # Skips placeholders if not filled
        if "INSERISCI_QUI" in webhook_url:
            continue
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending Discord notification: {e}")

def check_ddos():
    previous_status = load_status()
    current_status = {}

    for ip in TARGET_IPS:
        is_under_attack = False

        try:
            # Query OVH API for IP mitigation status
            ip_info = client.get(f'/ip/{ip}/mitigation/{ip}')
            
            # If automatic mitigation is active, IP is under attack
            if ip_info and ip_info.get('auto'):
                is_under_attack = True
        except ovh.exceptions.APIError:
            # API returns error/404 if no mitigation is active for the IP
            is_under_attack = False

        current_status[ip] = is_under_attack
        was_under_attack = previous_status.get(ip, False)

        # 1. ATTACK STARTED: Wasn't under attack before, but IS now
        if is_under_attack and not was_under_attack:
            send_discord_alert(
                title=" DDOS ATTACK DETECTED",
                description=f"A DDoS attack is currently ongoing on IP `{ip}`.\nOVH automatic mitigation is **ACTIVE**.",
                color=15158332,  # Red
                ip=ip
            )

        # 2. ATTACK ENDED: Was under attack before, but IS NOT anymore
        elif not is_under_attack and was_under_attack:
            send_discord_alert(
                title=" DDOS ATTACK ENDED",
                description=f"The DDoS attack on IP `{ip}` has ended.\nTraffic has returned to normal.",
                color=3066993,  # Green
                ip=ip
            )

    # Save current status to file
    save_status(current_status)

if __name__ == "__main__":
    check_ddos()