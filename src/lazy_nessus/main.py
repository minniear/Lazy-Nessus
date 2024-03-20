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

from requests import get, post, packages
from json import loads
from time import sleep, strftime, strptime
from sys import exit
from sys import path as sys_path
from os import remove, getenv
from os import path as os_path
from re import findall
from dotenv import load_dotenv
from argparse import ArgumentParser, Namespace
from xml.etree import ElementTree as ET
from pathlib import Path
from base64 import b64decode, b64encode

sys_path.append(os_path.dirname(os_path.dirname(os_path.abspath(__file__))))

from lazy_nessus.__about__ import __version__
from lazy_nessus.utils.spinner import Spinner
from lazy_nessus.scans.actions.pause import pause_action_args
from lazy_nessus.scans.actions.resume import resume_action_args
from lazy_nessus.scans.actions.list import list_action_args
from lazy_nessus.scans.actions.check import check_action_args
from lazy_nessus.scans.actions.export import export_action_args
from lazy_nessus.scans.actions.search import search_action_args

action_arg_funcs = [
    pause_action_args,
    resume_action_args,
    list_action_args,
    check_action_args,
    export_action_args,
    search_action_args,
]

# Disable SSL warnings
packages.urllib3.disable_warnings()
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


# Get environment variables from ~/.env
dotenv_path = os_path.join(os_path.expanduser("~"), ".env")
load_dotenv(dotenv_path)


def get_args() -> Namespace:
    parser = ArgumentParser(
        description="Pause, resume, list, search for, check the status of, or export a Nessus scan. There is also the option to schedule a pause or resume action. Telegram bot support is also included."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit",
    )
    category_subparsers = parser.add_subparsers(
        title="Categories", description="Available categories", required=True
    )

    scans = category_subparsers.add_parser("scans", help="Actions for scans")
    scans_actions_subparsers = scans.add_subparsers(
        dest="action", title="Actions", description="Available actions", required=True
    )

    # TODO: Adds subparser for each category of actions
    # policies = category_subparsers.add_parser("policies", help="Actions for policies")
    # credentials = category_subparsers.add_parser("credentials", help="Actions for credentials")
    # policies_actions_subparsers = policies.add_subparsers(dest="action", title="Actions", description="Available actions", required=True)
    # credentials_actions_subparsers = credentials.add_subparsers(dest="action", title="Actions", description="Available actions", required=True)

    std_parser = ArgumentParser(add_help=False)
    auth_group = std_parser.add_argument_group(
        "Authentication", "Authentication options"
    )
    auth_group.add_argument(
        "-aT",
        "--api_token",
        action="store",
        default=getenv("NESSUS_API_TOKEN"),
        help="Nessus API token (defaults to NESSUS_API_TOKEN in ~/.env file)",
        type=str,
    )
    auth_group.add_argument(
        "-c",
        "--x_cookie",
        action="store",
        default=getenv("NESSUS_X_COOKIE"),
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
        default=getenv("NESSUS_PASSWORD"),
        help="Nessus password (defaults to NESSUS_PASSWORD in ~/.env file)",
        type=str,
    )

    nessus_group = std_parser.add_argument_group("Nessus", "Nessus options")
    nessus_group.add_argument(
        "-S",
        "--server",
        action="store",
        help="Nessus server IP address or hostname (default: localhost)",
        default="localhost",
    )
    nessus_group.add_argument(
        "-P",
        "--port",
        required=False,
        action="store",
        help="Nessus server port (default: 8834)",
        default=8834,
    )

    for action_arg_func in action_arg_funcs:
        scans_actions_subparsers = action_arg_func(scans_actions_subparsers, std_parser)

    args = parser.parse_args()
    return args


def get_scan_status(args: Namespace) -> dict:
    """Get the status of a scan

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: Scan status
    """
    url = f"https://{args.server}:{args.port}/scans/{args.scan_id}"
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
    response = get(url, headers=headers, verify=False)
    scan = loads(response.text)
    if response.status_code != 200:
        return {
            "status": scan["error"],
            "name": "error",
            "response_code": response.status_code,
        }
    return {
        "status": scan["info"]["status"],
        "name": scan["info"]["name"],
        "response_code": response.status_code,
    }


def get_scans_list(args: Namespace) -> dict:
    """Get a list of scans

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: List of scans
    """
    url = f"https://{args.server}:{args.port}/scans"
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
    response = get(url, headers=headers, verify=False)
    scans = loads(response.text)
    if response.status_code != 200:
        return {
            "status": scans["error"],
            "name": "error",
            "response_code": response.status_code,
        }
    list = []
    for scan in scans["scans"]:
        list.append({"id": scan["id"], "name": scan["name"], "status": scan["status"]})

    return {"status": list, "name": "scans", "response_code": response.status_code}


def get_headers(args: Namespace) -> dict:
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
            response = get(url, verify=False)
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            exit(1)
        if response.status_code != 200:
            print_error(
                f'Status code {response.status_code} - {loads(response.text)["error"]}'
            )
            exit(1)
        if args.verbose:
            print_info(f"Obtained X-API-Token")
        api_token_regex = '"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"'
        token_header = findall(api_token_regex, response.text)[0].replace('"', "")
        headers = {"X-Cookie": f"token={args.x_cookie}", "X-API-Token": token_header}
    elif args.x_cookie == None and args.api_token != None and args.password == None:
        print_error("X-Cookie or password is required")
        exit(1)
    elif args.x_cookie == None and args.api_token != None and args.password != None:
        url = f"https://{args.server}:{args.port}/session"
        try:
            response = post(
                url,
                data={"username": args.username, "password": args.password},
                verify=False,
            )
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            exit(1)
        if response.status_code != 200:
            print_error(
                f'Status code {response.status_code} - {loads(response.text)["error"]}'
            )
            exit(1)
        if args.verbose:
            print_success(f"Username and password work!")
            print_info(f"Obtained X-Cookie")
        cookie_header = loads(response.text)["token"]
        headers = {"X-Cookie": f"token={cookie_header}", "X-API-Token": args.api_token}
    elif args.x_cookie == None and args.api_token == None and args.password != None:
        url = f"https://{args.server}:{args.port}/session"
        try:
            response = post(
                url,
                data={"username": args.username, "password": args.password},
                verify=False,
            )
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            exit(1)
        if response.status_code != 200:
            print_error(
                f'Status code {response.status_code} - {loads(response.text)["error"]}'
            )
            exit(1)
        if args.verbose:
            print_success(f"Username and password work!")
            print_info(f"Obtained X-Cookie")
        cookie_header = loads(response.text)["token"]
        url = f"https://{args.server}:{args.port}/nessus6.js"
        try:
            response = get(url, verify=False)
        except:
            print_error("Unable to connect to Nessus server. Check server IP and port")
            exit(1)
        if response.status_code != 200:
            print_error(
                f'Status code {response.status_code} - {loads(response.text)["error"]}'
            )
            exit(1)
        if args.verbose:
            print_info(f"Obtained X-API-Token")
        api_token_regex = '"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}"'
        token_header = findall(api_token_regex, response.text)[0].replace('"', "")
        headers = {"X-Cookie": f"token={cookie_header}", "X-API-Token": token_header}
    else:
        print_error("X-Cookie or password is required")
        exit(1)
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
        response = post(url, headers=headers, verify=False)
        if response.status_code != 200:
            print_error(
                f'Status code {response.status_code} - {loads(response.text)["error"]}'
            )
            if args.telegramToken and args.telegramChatID:
                telegram_bot_sendtext(
                    f"Nessus Error: {response.status_code} - Scan {args.scan_id} not {args.action}",
                    args,
                )
            exit(1)
    else:
        print_error('Invalid action specified (must be "pause" or "resume")')
        exit(1)


def telegram_bot_sendtext(bot_message: str, args: Namespace) -> None:
    """Send a message to a telegram bot

    Args:
        bot_message (str): Message to send
        args (Namespace): Arguments
    """
    # check if telegramToken and telegramChatID are set if action is not check
    if (
        args.telegramToken != None
        and args.telegramChatID != None
        and args.action not in ["check", "list"]
    ):
        telegram_message = bot_message.replace(" ", "%20")
        telegram_url = f"https://api.telegram.org/bot{args.telegramToken}/sendMessage?chat_id={args.telegramChatID}&text={telegram_message}"
        try:
            response = get(telegram_url)
        except:
            print("Error sending telegram message. Check token and chat ID")
            exit(1)


def isTimeFormat(input: str) -> bool:
    """Check if time is in the correct format

    Args:
        input (str): Time to check

    Returns:
        bool: True if time is in the correct format, False if not
    """
    try:
        strptime(input, TIME_FORMAT)
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
        formatted_time = strptime(input, TIME_FORMAT)
        return strftime(TIME_FORMAT, formatted_time)
    except ValueError:
        return False


def get_scan_export(args: Namespace) -> dict:
    """Get the export of a scan

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: Scan export
    """
    url_base = f"https://{args.server}:{args.port}/scans/{args.scan_id}/export"

    # get the export token and file
    url = url_base
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}

    if args.format == "nessus":
        body = {
            "format": "nessus",
        }
    elif args.format == "html":
        # get the template id because each environment has different template ids
        template_id = None
        url = f"https://{args.server}:{args.port}/reports/custom/templates"
        response = get(url, headers=headers, verify=False)
        data: list = loads(response.text)
        if response.status_code != 200:
            return {
                "status": data["error"],
                "name": "error",
                "response_code": response.status_code,
            }
        if args.verbose:
            print_success(f"X-API-Token and X-Cookie work!")
        # get the template id from a dict list of templates
        for template in data:
            # TODO: Make a list templates action
            if template["name"] == "Detailed Vulnerabilities By Plugin":
                template_id = template["id"]
                break
        # if template_id is not found then exit
        if template_id == None:
            return {
                "status": "No Detailed Vulnerabilities By Plugin template found",
                "name": "error",
                "response_code": response.status_code,
            }
        # set the payload
        body = {
            "format": "html",
            "template_id": template_id,
        }
        if args.verbose:
            print_info(f"Obtained template id")
    url = url_base
    response = post(url, headers=headers, verify=False, data=body)
    data = loads(response.text)
    if response.status_code != 200:
        return {
            "status": response.text,
            "name": "error",
            "response_code": response.status_code,
        }

    if args.verbose:
        print_info(f"Obtained export token and file")
    token, file = data["token"], data["file"]

    # check if export is ready
    url = f"https://{args.server}:{args.port}/tokens/{token}/status"
    response = get(url, headers=headers, verify=False)
    if response.status_code != 200:
        return {
            "status": response.text,
            "name": "error",
            "response_code": response.status_code,
        }
    data = loads(response.text)
    with Spinner(f"{INFO} INFO: Waiting for export to be ready...{RESET}"):
        while data["status"] != "ready":
            response = get(url, headers=headers, verify=False)
            data = loads(response.text)
            sleep(5)
    # without this print statement the text above it will be overwritten
    print()
    # download export
    url = f"https://{args.server}:{args.port}/tokens/{token}/download"
    if args.verbose:
        print_info(f"Downloading export")
    response = get(url, headers=headers, verify=False)
    if response.status_code != 200:
        return {
            "status": response.text,
            "name": "error",
            "response_code": response.status_code,
        }

    type = response.headers["Content-Type"]
    if type in ["text/xml", "text/html"]:
        appended_time = strftime("%Y-%m-%d_%H-%M-%S")
        # split after the first = sign
        filename_equals = response.headers["Content-Disposition"].split("=", 1)[1]
        # join the list back together and remove quotes
        filename_full = "".join(filename_equals).replace('"', "")
        # split after the first _ sign
        filename_base = filename_full.split("_")[0]
        # check if filename is base64 encoded
        if isBase64(filename_base):
            filename = b64decode(filename_base).decode("utf-8")
        else:
            filename = filename_base
        # append the time to the filename and add the extension
        filename = (
            f"{filename}_{appended_time}.html"
            if type == "text/html"
            else f"{filename}_{appended_time}.nessus"
        )
        data = {"filedata": response.text, "filename": filename}

        return {"status": data, "name": "export", "response_code": response.status_code}
    else:
        return {"status": type, "name": "error", "response_code": response.status_code}


def get_scan_search(args: Namespace) -> dict:
    """Get the scans that match the search string

    Args:
        args (Namespace): Arguments

    Returns:
        dict[str, str]: Scan search results
    """
    url = f"https://{args.server}:{args.port}/scans"
    headers = {"X-Api-Token": args.api_token, "X-Cookie": args.x_cookie}
    response = get(url, headers=headers, verify=False)
    scans = loads(response.text)
    if response.status_code != 200:
        return {
            "status": scans["error"],
            "name": "error",
            "response_code": response.status_code,
        }
    list = []
    for scan in scans["scans"]:
        search_string = args.search_string.lower()
        scan_name = scan["name"].lower()
        if search_string in scan_name:
            list.append(
                {"id": scan["id"], "name": scan["name"], "status": scan["status"]}
            )

    if len(list) == 0:
        return {
            "status": "No scans found",
            "name": "error",
            "response_code": response.status_code,
        }

    return {"status": list, "name": "scans", "response_code": response.status_code}


def isBase64(string) -> bool:
    """Check if string or bytes are base64 encoded

    Args:
        string (string or bytes): String or bytes to check

    Raises:
        ValueError: Argument must be string or bytes

    Returns:
        bool: True if string or bytes are base64 encoded, False if not
    """
    try:
        if isinstance(string, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(string, "ascii")
        elif isinstance(string, bytes):
            sb_bytes = string
        else:
            raise ValueError("Argument must be string or bytes")
        return b64encode(b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False


def export_scan(args: Namespace) -> None:
    """Export a scan

    Args:
        args (Namespace): Arguments
    """
    try:
        export = get_scan_export(args)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    if export["response_code"] != 200 or export["name"] == "error":
        raise Exception(
            f"Status code {export['response_code']} - Reason: {export['status']}"
        )
    # set the file name and data
    file_name = export["status"]["filename"]
    file_data = export["status"]["filedata"]
    # write the file
    try:
        with open(f"{file_name}", "w") as f:
            f.write(file_data)
    except:
        if Path(file_name).is_file():
            remove(file_name)
        raise Exception(f"Unable to write to file {file_name}")
    print_success(f"Exported scan to {file_name}")
    return


def main():
    args = get_args()

    formatted_time = None

    if args.action in ["pause", "resume"]:
        # check if time is specified and if it is in the correct format
        if args.time is not None and isTimeFormat(args.time) == False:
            print_error("Invalid time format (YYYY-MM-DD HH:MM)")
            exit(1)
        # check if time is specified and formatted close to the correct format
        elif args.time is not None and args.action not in ["check", "list"]:
            formatted_time = reformat_time(args.time)
            # if the time is in the past then exit
            if formatted_time < strftime(TIME_FORMAT):
                print_error("Time specified is in the past")
                exit(1)

    # get X-API-Token and X-Cookie
    headers = get_headers(args)
    args.api_token = headers["X-API-Token"]
    args.x_cookie = headers["X-Cookie"]

    # TODO: Make a stream for the export in case the file is too large
    if args.action == "export":
        try:
            if args.format == "both":
                args.format = "nessus"
                export_scan(args)
                args.format = "html"
                export_scan(args)
            else:
                export_scan(args)
        except KeyboardInterrupt:
            print_error("Exiting...")
            exit(1)
        except Exception as e:
            print_error(e)
            exit(1)
        exit(0)

    # list and search actions
    if args.action in ["list", "search"]:
        try:
            scans = (
                get_scans_list(args) if args.action == "list" else get_scan_search(args)
            )
        except KeyboardInterrupt:
            print_error("Exiting...")
            exit(1)
        response = scans["status"]
        response_name = scans["name"]
        response_code = scans["response_code"]
        if response_name == "error":
            print_error(f"Status code {response_code} - {response}")
            exit(1)
        if args.verbose:
            print_success(f"X-API-Token and X-Cookie work!")

        # print scan list with color coding
        print_info(f"{'ID':<10}{'Name':<70}{'Status':<10}")
        print_info(f"{'-'*10:<10}{'-'*70:<70}{'-'*10:<10}")
        for scan in response:
            if scan["status"] == "running":
                print_info(
                    f"{scan['id']:<10}{scan['name']:<70}{BOLD}{CYAN}{scan['status']:<10}{RESET}"
                )
            elif scan["status"] == "paused":
                print_info(
                    f"{scan['id']:<10}{scan['name']:<70}{BOLD}{PURPLE}{scan['status']:<10}{RESET}"
                )
            elif scan["status"] == "completed":
                print_info(
                    f"{scan['id']:<10}{scan['name']:<70}{BOLD}{GREEN}{scan['status']:<10}{RESET}"
                )
            elif scan["status"] == "canceled":
                print_info(
                    f"{scan['id']:<10}{scan['name']:<70}{BOLD}{RED}{scan['status']:<10}{RESET}"
                )
            else:
                print_info(
                    f"{scan['id']:<10}{scan['name']:<70}{BOLD}{scan['status']:<10}{RESET}"
                )
        exit(0)

    # get scan status
    try:
        check = get_scan_status(args)
    except KeyboardInterrupt:
        print_error("Exiting...")
        exit(1)
    status = check["status"]
    name = check["name"]
    response_code = check["response_code"]
    if response_code != 200:
        print_error(f"Status code {response_code} - {status}")
        exit(1)

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
        exit(0)

    # check if scan is running or paused and exit if it is already running or paused, except if scheduled
    if status == "running" and args.action == "resume" and formatted_time is None:
        print_error("Scan is already running")
        exit(1)
    elif status == "paused" and args.action == "pause" and formatted_time is None:
        print_error("Scan is already paused")
        exit(1)

    # Scheduled action handling
    if formatted_time is not None:
        telegram_bot_sendtext(
            f'Nessus: Scan "{name}" has been tasked to {args.action} at {formatted_time}',
            args,
        )
        if args.verbose:
            print_info(
                f'Scan "{name}" has been tasked to {args.action} at {formatted_time}'
            )
        while True:
            try:
                current_time = strftime("%Y-%m-%d %H:%M")
                if current_time == formatted_time:
                    break
                sleep(50)
            except KeyboardInterrupt:
                print_error("Exiting...")
                exit(1)

    # Perform action
    try:
        scan_actions(args)
    except KeyboardInterrupt:
        print_error("Exiting...")
        exit(1)

    now_time = strftime("%Y-%m-%d %H:%M")
    if args.verbose:
        if args.action == "pause":
            print_info(f'{args.action.capitalize().split("e")[0]}ing scan')
        elif args.action == "resume":
            # Cutt off the second "e" in resume and adding "ing" to the end
            temp = args.action.split("e")
            res = "e".join(temp[:2])
            print_info(f"{res.capitalize()}ing scan")

    # check if scan is running or paused and wait until the opposite is true
    while True:
        try:
            check = get_scan_status(args)
            status = check["status"]
            name = check["name"]
            response_code = check["response_code"]
            # Error handling
            if response_code != 200:
                print_error(f"Status code {response_code} - {status}")
                telegram_bot_sendtext(
                    f"Nessus Error: {response_code} - Scan {args.scan_id} not {args.action}d. Reason: {status}",
                    args,
                )
                exit(1)
            elif status == "running" and args.action == "pause":
                sleep(60)
            elif status == "paused" and args.action == "resume":
                sleep(60)
            else:
                break
        except KeyboardInterrupt:
            print_error("Exiting...")
            exit(1)
        except:
            print_error(
                "Nessus Error: Error getting scan status. Action may have failed"
            )
            telegram_bot_sendtext(
                f"Nessus Error: Error getting scan status for scan {args.scan_id}. Action may have failed",
                args,
            )
            exit(1)

    now_time = strftime("%Y-%m-%d %H:%M")
    print_success(f'Scan "{name}" {args.action}d')
    telegram_bot_sendtext(f"Nessus: Scan {name} {args.action}d at {now_time}", args)


if __name__ == "__main__":
    main()
