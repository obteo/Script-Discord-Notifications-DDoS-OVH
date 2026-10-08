# Script-Discord-Notifications-DDoS-OVH
Script to receive Discord notifications about DDoS attacks on OVH
# OVH DDoS Monitor – Discord Alerts

A lightweight Python script that monitors the OVHcloud Anti-DDoS mitigation status of multiple IP addresses and sends real-time attack notifications to Discord through webhooks.

The script uses the official OVHcloud API to detect when automatic DDoS mitigation is activated or deactivated.

It is designed to run automatically through a Linux cron job and supports multiple IP addresses and Discord webhooks.

## Features

- **OVHcloud API Integration** – Checks automatic Anti-DDoS mitigation status.
- **Multiple IP Monitoring** – Monitor several OVHcloud IP addresses simultaneously.
- **Discord Notifications** – Send alerts to one or more Discord channels using webhooks.
- **Attack Detection** – Receive a red Discord notification when an attack is detected.
- **Attack End Notifications** – Receive a green Discord notification when mitigation is no longer active.
- **Spam Prevention** – Stores previous attack states in a local JSON file to avoid repeated notifications.
- **Cron Job Support** – Automatically checks IP addresses every minute.
- **Lightweight** – Requires only Python and two external libraries.

## Requirements

- Linux server (Debian 12/13, Ubuntu, or similar)
- Python 3
- Internet connectivity
- OVHcloud account with API access
- One or more Discord webhook URLs

## 1. Install Dependencies

Update your system and install the required packages:

```bash
apt update
apt install -y python3 python3-pip python3-venv
```

Create a dedicated Python virtual environment:

```bash
python3 -m venv /root/ovh_env
```

Install the required Python libraries:

```bash
/root/ovh_env/bin/pip install requests ovh
```

## 2. Download and Configure the Script

Save the Python script as:

```text
/root/Script_Monitoraggio_DDoS_OVH.py
```

Edit the script:

```bash
nano /root/Script_Monitoraggio_DDoS_OVH.py
```

### Discord Webhooks

Create a webhook in your Discord server:

**Server Settings → Integrations → Webhooks → New Webhook**

Copy the webhook URL and add it to the script:

```python
DISCORD_WEBHOOKS = [
    "https://discord.com/api/webhooks/YOUR_FIRST_WEBHOOK",
    "https://discord.com/api/webhooks/YOUR_SECOND_WEBHOOK"
]
```

You can configure one or multiple webhook URLs.

Each configured webhook receives the same notifications.

### OVHcloud API Credentials

Generate your API credentials using:

https://eu.api.ovh.com/createToken/

Configure the following variables:

```python
APPLICATION_KEY = "YOUR_APPLICATION_KEY"
APPLICATION_SECRET = "YOUR_APPLICATION_SECRET"
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
```

Grant the API credentials the following permission:

```text
GET /ip/*
```

Use the OVHcloud API region corresponding to your account. By default, the script uses:

```python
endpoint='ovh-eu'
```

### IP Addresses to Monitor

Add the public IP addresses you want to monitor:

```python
TARGET_IPS = [
    "192.0.2.10",
    "192.0.2.20",
    "192.0.2.30"
]
```

Only configure IP addresses accessible through your OVHcloud account.

### Status File

The script stores the last known mitigation state in:

```python
STATUS_FILE = "/root/ddos_status.json"
```

Example content:

```json
{
    "192.0.2.10": false,
    "192.0.2.20": true,
    "192.0.2.30": false
}
```

- `true` – OVH automatic mitigation is active.
- `false` – OVH automatic mitigation is not reported as active.

The file is created automatically after the first execution.

This mechanism prevents sending the same alert every minute.

## 3. Run the Script Manually

Execute the script using the Python virtual environment:

```bash
/root/ovh_env/bin/python3 /root/Script_Monitoraggio_DDoS_OVH.py
```

If the script runs successfully, it saves the current mitigation status.

**Important:** The script sends notifications only when it detects a change in status. It does not send a notification simply because the script was executed.

If mitigation is already active during the first run, an attack notification will be sent.

## 4. Configure the Cron Job

To automatically monitor your IP addresses every minute, configure a cron job.

Install cron if necessary:

```bash
apt install -y cron
systemctl enable --now cron
```

Open the root crontab:

```bash
crontab -e
```

Add the following line:

```cron
* * * * * /root/ovh_env/bin/python3 /root/Script_Monitoraggio_DDoS_OVH.py >> /var/log/ovh_ddos_discord.log 2>&1
```

Save and exit.

The script will now execute automatically every minute.

### Verify the Cron Job

Check your scheduled tasks:

```bash
crontab -l
```

Check whether cron is running:

```bash
systemctl status cron
```

View the script logs:

```bash
tail -f /var/log/ovh_ddos_discord.log
```

**Note:** The script does not log successful checks by default. An empty log file does not necessarily indicate a problem.

## 5. Discord Notifications

### DDoS Attack Detected

When OVHcloud reports automatic mitigation activation, the script sends a red Discord embed:

**DDOS ATTACK DETECTED**

A DDoS attack is currently ongoing on IP `192.0.2.10`.

OVH automatic mitigation is **ACTIVE**.

### DDoS Attack Ended

When the previously detected mitigation is no longer active, the script sends a green Discord embed:

**DDOS ATTACK ENDED**

The DDoS attack on IP `192.0.2.10` has ended.

Traffic has returned to normal.

Notifications are delivered to every configured Discord webhook.

## 6. How It Works

Every time the script runs:

1. Loads the previous IP mitigation states from the JSON status file.
2. Connects to the OVHcloud API.
3. Checks the mitigation status of every configured IP address.
4. Compares the current state against the previous state.
5. Sends an attack-start notification when mitigation changes from inactive to active.
6. Sends an attack-end notification when mitigation changes from active to inactive.
7. Saves the current status for the next execution.

If the mitigation status remains unchanged, no Discord notification is sent.

## 7. Troubleshooting

### No Discord Notifications

Verify that:

- Discord webhook URLs are correct.
- OVHcloud API credentials are valid.
- The configured IP addresses belong to your account.
- The API token has the required permissions.
- The server can reach Discord and OVHcloud.

Also remember that notifications are only sent when the mitigation status changes.

### Missing Python Modules

If you receive:

```text
ModuleNotFoundError: No module named 'ovh'
```

Install the dependencies:

```bash
/root/ovh_env/bin/pip install requests ovh
```

### Cron Job Not Executing

Verify the script path:

```bash
ls -l /root/Script_Monitoraggio_DDoS_OVH.py
```

Run it manually:

```bash
/root/ovh_env/bin/python3 /root/Script_Monitoraggio_DDoS_OVH.py
```

Check cron:

```bash
systemctl status cron
```

### Reset Monitoring State

To reset saved mitigation states:

```bash
rm -f /root/ddos_status.json
```

The file will be recreated on the next execution.

**Warning:** Resetting the file may trigger a new notification for IP addresses with active mitigation.

## 8. Security Recommendations

- Never publish real OVHcloud API credentials.
- Never share Discord webhook URLs publicly.
- Keep credentials out of public Git repositories.
- Use read-only API permissions whenever possible.
- Restrict access to the script and configuration files.
- Rotate credentials immediately if they are accidentally exposed.

Recommended file permissions:

```bash
chmod 600 /root/Script_Monitoraggio_DDoS_OVH.py
chmod 600 /root/ddos_status.json
```

## 9. Limitations

This script monitors the OVHcloud automatic mitigation status, not network traffic directly.

An active mitigation state can indicate DDoS protection is engaged, but the script does not independently verify the attack or determine its severity.

The script uses polling rather than push notifications, so alerts may be delayed by up to approximately one cron interval, plus API and execution latency.

API errors are currently treated as an inactive mitigation state. This may produce incorrect attack-end notifications during temporary API failures. For production environments, API errors should be handled separately so that the last confirmed mitigation state is preserved.

Discord delivery failures are logged to standard output but are not automatically retried.

## License

You are free to adapt this script for your own infrastructure, subject to any license terms attached to the distributed source code.

---

**OVHcloud DDoS Monitor – Python + Discord Webhooks**

A simple solution for monitoring OVHcloud Anti-DDoS mitigation status directly from your Discord server.
