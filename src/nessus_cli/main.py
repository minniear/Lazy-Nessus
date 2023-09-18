#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Nessus CLI
# Copyright (C) <2023>  <Luke Minniear>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import requests
import json
import time
import sys
import os
import re
from dotenv import load_dotenv
from argparse import ArgumentParser, Namespace
from xml.etree import ElementTree as ET
from pathlib import Path

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()
INFO = "\033[93m[!]"
ERR = "\033[91m[-]"
SUCCESS = "\033[92m[+]"
RESET = "\033[0m"
BOLD = "\033[1m"

PURPLE = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"

TIME_FORMAT = "%Y-%m-%d %H:%M"


def print_info(message: str) -> None:
    """Print an info message

    Args:
        message (str): Message to print
    """
    print(f"{INFO} INFO: {message}{RESET}")


def print_error(message: str) -> None:
    """Print an error message

    Args:
        message (str): Message to print
    """
    print(f"{ERR} ERROR: {message}{RESET}")


def print_success(message: str) -> None:
    """Print a success message

    Args:
        message (str): Message to print
    """
    print(f"{SUCCESS} SUCCESS: {message}{RESET}")


dotenv_path = "~/.env"
load_dotenv(dotenv_path)


# TODO: Adds subparser for each action
def get_args() -> Namespace:
    parser = ArgumentParser(description="Pause, resume, list, check the status of, or export a Nessus scan. There is also the option to schedule a pause or resume action. Telegram bot support is also included.")
    nessus_group = parser.add_argument_group("Nessus")
    nessus_group.add_argument(
        "-S",
        "--server",
        action="store",
        help="Nessus server IP address or hostname (default: localhost)",
        default="localhost",
    )
    nessus_group.add_argument(
        "-P", "--port", required=False, action="store", help="Nessus server port (default: 8834)", default=8834
    )
    nessus_group.add_argument("-s", "--scan_id", action="store", help="Nessus scan ID")
    nessus_group.add_argument(
        "-a",
        "--action",
        required=True,
        action="store",
        help="Action to perform",
        type=str,
        choices=["pause", "resume", "check", "list", "export_nessus"],
    )
    nessus_group.add_argument(
        "-t",
        "--time",
        action="store",
        help="Time to pause or resume the scan. Only used with pause or resume actions (format: YYYY-MM-DD HH:MM)",
    )
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "-aT",
        "--api_token",
        action="store",
        default=os.getenv("NESSUS_API_TOKEN"),
        help="Nessus API token (defaults to NESSUS_API_TOKEN in ~/.env file)",
        type=str,
    )
    auth_group.add_argument(
        "-c",
        "--x_cookie",
        action="store",
        default=os.getenv("NESSUS_X_COOKIE"),
        help="Nessus X-Cookie (defaults to NESSUS_X_COOKIE in ~/.env file)",
        type=str,
    )
    auth_group.add_argument(
        "-u",
        "--username",
        action="store",
        default="root",
        help="Nessus username (defaults to root)",
        type=str,
    )
    auth_group.add_argument(
        "-p",
        "--password",
        action="store",
        default=os.getenv("NESSUS_PASSWORD"),
        help="Nessus password (defaults to NESSUS_PASSWORD in ~/.env file)",
        type=str,
    )
    telegram_group = parser.add_argument_group("Telegram")
    telegram_group.add_argument(
        "-tT",
        "--telegramToken",
        action="store",
        default=os.getenv("TELEGRAM_BOT_TOKEN"),
        help="Telegram bot token (defaults to TELEGRAM_BOT_TOKEN in ~/.env file)",
        type=str,
    )
    telegram_group.add_argument(
        "-tC",
        "--telegramChatID",
        action="store",
        default=os.getenv("TELEGRAM_CHAT_ID"),
        help="Telegram chat ID (defaults to TELEGRAM_CHAT_ID in ~/.env file)",
        type=str,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    return args


def get_scan_status(args: Namespace) -> dict[str, str]:
    """Get the status of a scan

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: Scan status
    """
    url = f"https://{args.server}:{args.port}/scans/{args.scan_id}"
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
    response = requests.get(url, headers=headers, verify=False)
    scan = json.loads(response.text)
    if response.status_code != 200:
        return {"status": scan["error"], "name": "error", "response_code": response.status_code}
    return {"status": scan["info"]["status"], "name": scan["info"]["name"], "response_code": response.status_code}


def get_scans_list(args: Namespace) -> dict[str, str]:
    """Get a list of scans

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: List of scans
    """
    url = f"https://{args.server}:{args.port}/scans"
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
    response = requests.get(url, headers=headers, verify=False)
    scans = json.loads(response.text)
    if response.status_code != 200:
        return {"status": scans["error"], "name": "error", "response_code": response.status_code}
    list = []
    for scan in scans["scans"]:
        list.append({"id": scan["id"], "name": scan["name"], "status": scan["status"]})

    return {"status": list, "name": "scans", "response_code": response.status_code}


def get_headers(args: Namespace) -> dict[str, str]:
    """Get X-API-Token and X-Cookie

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: X-API-Token and X-Cookie
    """
    if args.x_cookie != None and args.api_token != None:
        headers = {"X-Cookie": f"token={args.x_cookie}", "X-API-Token": args.api_token}
    elif args.x_cookie != None and args.api_token == None:
        url = f"https://{args.server}:{args.port}/nessus6.js"
        try:
            response = requests.get(url, verify=False)
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            sys.exit(1)
        if response.status_code != 200:
            print_error(f'Status code {response.status_code} - {json.loads(response.text)["error"]}')
            sys.exit(1)
        if args.verbose:
            print_info(f"Obtained X-API-Token")
        api_token_regex = '"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"'
        token_header = re.findall(api_token_regex, response.text)[0].replace('"', "")
        headers = {"X-Cookie": f"token={args.x_cookie}", "X-API-Token": token_header}
    elif args.x_cookie == None and args.api_token != None and args.password == None:
        print_error("X-Cookie or password is required")
        sys.exit(1)
    elif args.x_cookie == None and args.api_token != None and args.password != None:
        url = f"https://{args.server}:{args.port}/session"
        try:
            response = requests.post(url, data={"username": args.username, "password": args.password}, verify=False)
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            sys.exit(1)
        if response.status_code != 200:
            print_error(f'Status code {response.status_code} - {json.loads(response.text)["error"]}')
            sys.exit(1)
        if args.verbose:
            print_success(f"Username and password work!")
            print_info(f"Obtained X-Cookie")
        cookie_header = json.loads(response.text)["token"]
        headers = {"X-Cookie": f"token={cookie_header}", "X-API-Token": args.api_token}
    elif args.x_cookie == None and args.api_token == None and args.password != None:
        url = f"https://{args.server}:{args.port}/session"
        try:
            response = requests.post(url, data={"username": args.username, "password": args.password}, verify=False)
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            sys.exit(1)
        if response.status_code != 200:
            print_error(f'Status code {response.status_code} - {json.loads(response.text)["error"]}')
            sys.exit(1)
        if args.verbose:
            print_success(f"Username and password work!")
            print_info(f"Obtained X-Cookie")
        cookie_header = json.loads(response.text)["token"]
        url = f"https://{args.server}:{args.port}/nessus6.js"
        try:
            response = requests.get(url, verify=False)
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            sys.exit(1)
        if response.status_code != 200:
            print_error(f'Status code {response.status_code} - {json.loads(response.text)["error"]}')
            sys.exit(1)
        if args.verbose:
            print_info(f"Obtained X-API-Token")
        api_token_regex = '"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"'
        token_header = re.findall(api_token_regex, response.text)[0].replace('"', "")
        headers = {"X-Cookie": f"token={cookie_header}", "X-API-Token": token_header}
    else:
        print_error("X-Cookie or password is required")
        sys.exit(1)
    return headers


def scan_actions(args: Namespace) -> None:
    """Pause or resume a scan

    Args:
        args (Namespace): Arguments
    """
    if args.action == "pause" or args.action == "resume":
        if args.telegramToken and args.telegramChatID and args.verbose:
                telegram_bot_sendtext(
                    f"Nessus: Scan {args.scan_id} is being {args.action}d", args
                )
        url = f"https://{args.server}:{args.port}/scans/{args.scan_id}/{args.action}"
        headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
        response = requests.post(url, headers=headers, verify=False)
        if response.status_code != 200:
            print_error(f'Status code {response.status_code} - {json.loads(response.text)["error"]}')
            if args.telegramToken and args.telegramChatID:
                telegram_bot_sendtext(
                    f"Nessus Error: {response.status_code} - Scan {args.scan_id} not {args.action}", args
                )
            sys.exit(1)
    else:
        print_error('Invalid action specified (must be "pause" or "resume")')
        sys.exit(1)


def telegram_bot_sendtext(bot_message: str, args: Namespace) -> None:
    """Send a message to a telegram bot

    Args:
        bot_message (str): Message to send
        args (Namespace): Arguments
    """
    # check if telegramToken and telegramChatID are set if action is not check
    if args.telegramToken != None and args.telegramChatID != None and args.action not in ["check", "list"]:
        telegram_message = bot_message.replace(" ", "%20")
        telegram_url = f"https://api.telegram.org/bot{args.telegramToken}/sendMessage?chat_id={args.telegramChatID}&text={telegram_message}"
        try:
            response = requests.get(telegram_url)
        except:
            print("Error sending telegram message. Check token and chat ID")
            sys.exit(1)


def isTimeFormat(input: str) -> bool:
    """Check if time is in the correct format

    Args:
        input (str): Time to check

    Returns:
        bool: True if time is in the correct format, False if not
    """
    try:
        time.strptime(input, TIME_FORMAT)
        return True
    except ValueError:
        return False


def reformat_time(input: str) -> str:
    """Reformat time to the correct format

    Args:
        input (str): Time to reformat

    Returns:
        str: Reformatted time if successful, False if not
    """
    try:
        formatted_time = time.strptime(input, TIME_FORMAT)
        return time.strftime(TIME_FORMAT, formatted_time)
    except ValueError:
        return False

def get_scan_export(args: Namespace):
    """Get a list of scans

    Args:
        args (Namespace): Arguments

    Returns:
        
    """
    url_base = f"https://{args.server}:{args.port}/scans/{args.scan_id}/export"
    
    # get the export token and file
    url = url_base
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
    body = {
        "format": "nessus"
    }
    response = requests.post(url, headers=headers, verify=False, data=body)
    data = json.loads(response.text)
    if response.status_code != 200:
        return {"status": response.text, "name": "error", "response_code": response.status_code}
    
    if args.verbose:
        print_success(f"X-API-Token and X-Cookie work!")
        print_info(f"Obtained export token and file")
    token,file = data["token"], data["file"]
    
    # check if export is ready
    url = f"{url_base}/{file}/status"
    response = requests.get(url, headers=headers, verify=False)
    data = json.loads(response.text)
    while data["status"] != "ready":
        response = requests.get(url, headers=headers, verify=False)
        data = json.loads(response.text)
        if args.verbose:
            print_info(f"Waiting for export to be ready..")
        time.sleep(5)
        
    # download export
    url = f"{url_base}/{file}/download"
    if args.verbose:
        print_info(f"Downloading export")
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        return {"status": response.text, "name": "error", "response_code": response.status_code}
    
    type = response.headers["Content-Type"]
    if type == "application/octet-stream":
        filename = response.headers["Content-Disposition"].split("=")[1]
        data = {"xml": response.text, "filename": filename}
        # data = ET.fromstring(response.text)
        # data = ET.tostring(data, encoding='utf8', method='xml')
        return {"status": data, "name": "export", "response_code": response.status_code}
    else:
        return {"status": type, "name": "error", "response_code": response.status_code}

def main():
    args = get_args()

    formatted_time = None

    if args.action not in ["check", "list", "export_nessus"]:
        # check if time is specified and if it is in the correct format
        if args.time is not None and isTimeFormat(args.time) == False:
            print_error("Invalid time format (YYYY-MM-DD HH:MM)")
            sys.exit(1)
        # check if time is specified and formatted close to the correct format
        elif args.time is not None and args.action not in ["check", "list"]:
            formatted_time = reformat_time(args.time)
            # if the time is in the past then exit
            if formatted_time < time.strftime(TIME_FORMAT):
                print_error("Time specified is in the past")
                sys.exit(1)

    # check if scan_id is specified for all actions except list before getting headers
    if args.action not in ["list"]:
        if args.scan_id is None:
            print_error("Scan ID is required to run that action")
            sys.exit(1)

    # get X-API-Token and X-Cookie
    headers = get_headers(args)
    args.api_token = headers["X-API-Token"]
    args.x_cookie = headers["X-Cookie"]
    
    # TODO: Make a stream for the export in case the file is too large
    if args.action == "export_nessus":
        export = get_scan_export(args)
        if export["response_code"] != 200 or export["name"] == "error":
            print_error(f"Status code {export['response_code']} - Content type: {export['status']}")
            sys.exit(1)
                
        filename = export["status"]["filename"]
        # remove quotes from filename
        filename = filename.replace('"', "")
        xml = export["status"]["xml"]
        
        if Path(filename).is_file():
            # if file exists then append the time to the end of the filename
            time = time.strftime("%Y-%m-%d_%H-%M-%S")
            filename_without_nessus = filename.split(".")[0]
            filename = f"{filename_without_nessus}_{time}.nessus"
            
        try:
            with open(f"{filename}", "w") as f:
                f.write(xml)
        except:
            print_error(f"Unable to write to file {filename}")
            if Path(filename).is_file():
                os.remove(filename)
            sys.exit(1)
            
        print_success(f"Exported scan to {filename}")
        sys.exit(0)
        
    # list scans
    if args.action == "list":
        scans = get_scans_list(args)
        response_code = scans["response_code"]
        response = scans["status"]
        if response_code != 200:
            print_error(f"Status code {response_code} - {response}")
            sys.exit(1)
        if args.verbose:
            print_success(f"X-API-Token and X-Cookie work!")
        
        # print scan list with color coding
        print_info(f"{'ID':<10}{'Name':<70}{'Status':<10}")
        print_info(f"{'-'*10:<10}{'-'*70:<70}{'-'*10:<10}")
        for scan in response:
            if scan['status'] == "running":
                print_info(f"{scan['id']:<10}{scan['name']:<70}{BOLD}{CYAN}{scan['status']:<10}{RESET}")
            elif scan['status'] == "paused":
                print_info(f"{scan['id']:<10}{scan['name']:<70}{BOLD}{PURPLE}{scan['status']:<10}{RESET}")
            elif scan['status'] == "completed":
                print_info(f"{scan['id']:<10}{scan['name']:<70}{BOLD}{GREEN}{scan['status']:<10}{RESET}")
            elif scan['status'] == "canceled":
                print_info(f"{scan['id']:<10}{scan['name']:<70}{BOLD}{RED}{scan['status']:<10}{RESET}")
            else:
                print_info(f"{scan['id']:<10}{scan['name']:<70}{BOLD}{scan['status']:<10}{RESET}")
        sys.exit(0)

    # get scan status
    check = get_scan_status(args)
    status = check["status"]
    name = check["name"]
    response_code = check["response_code"]
    if response_code != 200:
        print_error(f"Status code {response_code} - {status}")
        sys.exit(1)

    if args.verbose:
        print_success(f"X-API-Token and X-Cookie work!")
        
    # print scan status with color coding
    if status == "running":
        print_info(f'Scan "{name}" status: {BOLD}{CYAN}{status}{RESET}')
    elif status == "paused":
        print_info(f'Scan "{name}" status: {BOLD}{PURPLE}{status}{RESET}')
    elif status == "completed":
        print_info(f'Scan "{name}" status: {BOLD}{GREEN}{status}{RESET}')
    elif status == "canceled":
        print_info(f'Scan "{name}" status: {BOLD}{RED}{status}{RESET}')
    else:
        print_info(f'Scan "{name}" status: {BOLD}{status}{RESET}')

    # if it was just a check then exit else continue
    if args.action == "check":
        sys.exit(0)

    # check if scan is running or paused and exit if it is already running or paused, except if scheduled
    if status == "running" and args.action == "resume" and formatted_time is None:
        print_error("Scan is already running")
        sys.exit(1)
    elif status == "paused" and args.action == "pause" and formatted_time is None:
        print_error("Scan is already paused")
        sys.exit(1)

    # Scheduled action handling
    if formatted_time is not None:
        telegram_bot_sendtext(f'Nessus: Scan "{name}" has been tasked to {args.action} at {formatted_time}', args)
        if args.verbose:
            print_info(f'Scan "{name}" has been tasked to {args.action} at {formatted_time}')
        while True:
            current_time = time.strftime("%Y-%m-%d %H:%M")
            if current_time == formatted_time:
                break
            time.sleep(50)

    # Perform action
    scan_actions(args)
    now_time = time.strftime("%Y-%m-%d %H:%M")
    if args.verbose:
        if args.action == "pause":
            print_info(f'{args.action.capitalize().split("e")[0]}ing scan')
        elif args.action == "resume":
            # Cutt off the second "e" in resume and adding "ing" to the end
            temp = args.action.split("e")
            res = "e".join(temp[:2]) 
            print_info(f'{res.capitalize()}ing scan')

    # check if scan is running or paused and wait until the opposite is true
    while True:
        check = get_scan_status(args)
        status = check["status"]
        name = check["name"]
        response_code = check["response_code"]
        # Error handling
        if response_code != 200:
            print_error(f"Status code {response_code} - {status}")
            telegram_bot_sendtext(
                f"Nessus Error: {response_code} - Scan {args.scan_id} not {args.action}d. Reason: {status}", args
            )
            sys.exit(1)
        elif status == "running" and args.action == "pause":
            time.sleep(60)
        elif status == "paused" and args.action == "resume":
            time.sleep(60)
        else:
            break

    now_time = time.strftime("%Y-%m-%d %H:%M")
    print_success(f'Scan "{name}" {args.action}d')
    telegram_bot_sendtext(f"Nessus: Scan {name} {args.action}d at {now_time}", args)


if __name__ == "__main__":
    main()