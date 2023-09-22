# Lazy-Nessus

## Description
I made this script for me to not have to log into Nessus every time I wanted to pause/resume a scan because I am lazy and I don't like logging into my computer at 3 AM. I also added Telegram support since I'm paranoid and want to make sure my actions actually worked.

What started as a simple script to pause/resume scans has turned into a full-fledged CLI tool for Nessus. I have added the ability to list scans, check the status of a scan, export a scan, search for a scan, pause a scan, and resume a scan. I have also added the ability to use a .env file to store your API keys and other variables. This is useful if you want to use the Telegram bot functionality. I have also added the ability to pass all variables as command line arguments if you do not want to use a .env file.


## Requirements
- Python 3
- Nessus Professional or Nessus Manager
- Telegram Bot (optional)

## Installation
1. Pip install the script
```bash
pip3 install lazy-nessus
```
or
```bash
pip install lazy-nessus
```
2. Create a Telegram Bot (optional)
3. Create a .env file in your home directory and add your API keys and other variables (see below) (optional)
4. Run the script

## Development
1. Clone this repository
```bash
git clone https://github.com/minniear/lazy-nessus.git
```
2. Install the requirements, preferably in a virtual environment
```bash
python3 -m venv lazy-nessus
cd lazy-nessus
source bin/activate
pip3 install -r requirements.txt
```
3. Create a Telegram Bot (optional)
4. Create a .env file in your home directory and add your API keys and other variables (see below) (optional)
5. Run the script

## Examples
List all scans
```bash
lazy-nessus scans list
```
Check the status or a single scan on a given server
```bash
lazy-nessus scans check -S 192.168.250.158 -s 13
```
Pause a scan at a specific time with known API token and X-Cookie
```bash
lazy-nessus scans pause -S 10.10.10.10 -p 8080 -s 11 -t "2021-01-01 00:00" -tT "1234567890:ABCDEF1234567890" -tC "1234567890" -aT "1a2b3c4d-1a2b-3c4d-1a2b-3c4d1a2b3c4d" -c "1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d" -v
```
Resume a localhost scan at a specific time using a password
```bash
lazy-nessus scans resume -p 8080 -s 11 -t "2021-01-01 09:45" -p "1a2b3c4d5e6f7g8h9i0j"
```
Export a scan as a .nessus file
```bash
lazy-nessus scans export -f nessus -s 4 -p "1a2b3c4d5e6f7g8h9i0j"
```
Search for a scan by name
```bash
lazy-nessus scans search -s "Scan Name"
```
## Example .env file
All optional variables are added. If you do not want to use the .env file, you can pass the variables as command line arguments.
```
TELEGRAM_BOT_TOKEN="1234567890:ABCDEF1234567890"
TELEGRAM_CHAT_ID="1234567890"
NESSUS_API_TOKEN="1a2b3c4d-1a2b-3c4d-1a2b-3c4d1a2b3c4d"
NESSUS_X_COOKIE="1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d"
NESSUS_PASSWORD="1a2b3c4d5e6f7g8h9i0j"
```


## How to obtain the Nessus API token and X-Cookie
1. Log into Nessus
2. Open the developer tools in your browser
3. Go to the Network tab
4. Click on something like "All Scans" or "My Scans" under FOLDERS
5. Look for the GET request to **folders** and click on it
6. From the Headers tab, copy the X-Cookie value **AFTER** "token=" and paste it into the .env file
7. From the Headers tab, copy the X-API-Token value and paste it into the .env file
8. Also note the scan ID from the URL (e.g. https://nessus.example.com/#/scans/reports/11/hosts)

## How to obtain the Telegram bot token and chat ID
1. Start a chat with the BotFather
2. Send the BotFather the start message `/start`
3. Send the BotFather the newbot message `/newbot`
4. Answer the BotFather's questions to finsh setting up the bot. Keep in mind that your bot name will be searchable by all Telegram users.
5. Save your bot's API key for future reference.
6. Start a chat with your bot and then navigate to <https://api.telegram.org/bot123456789:jbd78sadvbdy63d37gda37bd8/getUpdates> and replace your API key in the URL. **IT NEEDS TO START WITH 'bot' SO KEEP THAT PART OF THE URL**.
7. You will likely get a blank result until you send your bot another message and refresh the getUpdates URL.
8. Once you see updates from the URL, note your 'chat_id'. You can use the combination of chat ID and your API key to send automated alerts.
    - EXAMPLE: `curl "https://api.telegram.org/bot123456789:jbd78sadvbdy63d37gda37bd8/sendMessage?chat_id=123456&text=%22You just got a shell! Go check your C2 server!%22"`
9. Copy the "id" value and paste it into the .env file
10. Copy the "token" value and paste it into the .env file




