# Schedule Nessus

## Description
I made this script for me to not have to log into Nessus every time I wanted to pause/resume a scan because I am lazy and I don't like logging into my computer at 3 AM. You can use this script to pause/resume a scan at a specific time, check if a scan is paused or running, or pause/resume a scan immediately all from the comfort of your terminal. You can also send Telegram notifications when a scan has been paused/resumed in case you are paranoid like me and want to make sure it actually happened.


## Requirements
- Python 3
- Nessus Professional or Nessus Manager
- Telegram Bot (optional)

# Installation Locally


## Development
1. Clone this repository
```bash
git clone https://github.com/minniear/schedule-nesssus.git
```
2. Install the requirements, preferably in a virtual environment
> NOTE: Not needed if you are using this script on RIVA laptops. All requirements are already installed.
```bash
python3 -m venv schedule-nessus
cd schedule-nessus
source bin/activate
pip3 install -r requirements.txt
```
3. Create a Telegram Bot (optional)
4. Create a .env file in your home directory and add your API keys and other variables (see below) (optional)
5. Run the script

## Usage
```
usage: nessus-cli [-h] [-S SERVER] [-P PORT] [-s SCAN_ID] -a {pause,resume,check,list,export_nessus} [-t TIME] [-aT API_TOKEN] [-c X_COOKIE] [-u USERNAME] [-p PASSWORD]
                          [-tT TELEGRAMTOKEN] [-tC TELEGRAMCHATID] [-v]

Pause, resume, list, check the status of, or export a Nessus scan. There is also the option to schedule a pause or resume action. Telegram bot support is also included.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose output

Nessus:
  -S SERVER, --server SERVER
                        Nessus server IP address or hostname (default: localhost)
  -P PORT, --port PORT  Nessus server port (default: 8834)
  -s SCAN_ID, --scan_id SCAN_ID
                        Nessus scan ID
  -a {pause,resume,check,list,export_nessus}, --action {pause,resume,check,list,export_nessus}
                        Action to perform
  -t TIME, --time TIME  Time to pause or resume the scan. Only used with pause or resume actions (format: YYYY-MM-DD HH:MM)

Authentication:
  -aT API_TOKEN, --api_token API_TOKEN
                        Nessus API token (defaults to NESSUS_API_TOKEN in .env file)
  -c X_COOKIE, --x_cookie X_COOKIE
                        Nessus X-Cookie (defaults to NESSUS_X_COOKIE in .env file)
  -u USERNAME, --username USERNAME
                        Nessus username (defaults to root)
  -p PASSWORD, --password PASSWORD
                        Nessus password (defaults to NESSUS_PASSWORD in .env file)

Telegram:
  -tT TELEGRAMTOKEN, --telegramToken TELEGRAMTOKEN
                        Telegram bot token (defaults to TELEGRAM_BOT_TOKEN in .env file)
  -tC TELEGRAMCHATID, --telegramChatID TELEGRAMCHATID
                        Telegram chat ID (defaults to TELEGRAM_CHAT_ID in .env file)
```
## Examples
List all scans
```bash
nessus-cli -a list
```
Check the status or a single scan on a given server
```bash
nessus-cli -S 192.168.250.158 -s 13 -a check
```
Pause a scan at a specific time with known API token and X-Cookie
```bash
nessus-cli -S 10.10.10.10 -p 8080 -s 11 -a pause -t "2021-01-01 00:00" -tT "1234567890:ABCDEF1234567890" -tC "1234567890" -aT "1a2b3c4d-1a2b-3c4d-1a2b-3c4d1a2b3c4d" -c "1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d1a2b3c4d" -v
```
Resume a localhost scan at a specific time using a password
```bash
nessus-cli -p 8080 -s 11 -a resume -t "2021-01-01 09:45" -p "1a2b3c4d5e6f7g8h9i0j"
```
Export a scan as a .nessus file
```bash
nessus-cli -s 4 -a export_nessus -p "1a2b3c4d5e6f7g8h9i0j"
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




