import os 
from argparse import ArgumentParser, _SubParsersAction
def pause_action_args(parser: _SubParsersAction, std_parser: ArgumentParser) -> _SubParsersAction:
    """
    Add arguments for the pause action to a _SubParsersAction[ArgumentParser]
    
    Args:
        parser (_SubParsersAction[ArgumentParser]): The subparser object
        std_parser (ArgumentParser): The standard parser object
        
    Returns:
        _SubParsersAction[ArgumentParser]: The parsed arguments
    """
    pause_parser = parser.add_parser("pause", help="Pause a scan", parents=[std_parser])
    
    telegram_group = pause_parser.add_argument_group("Telegram", "Telegram options")
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
    
    required_groug = pause_parser.add_argument_group("Required", "Required arguments")
    required_groug.add_argument(
        "-s",
        "--scan_id",
        action="store",
        help="Scan ID to pause",
        type=int,
        required=True,
    )
    
    optional_group = pause_parser.add_argument_group("Optional", "Optional arguments")
    optional_group.add_argument(
        "-t",
        "--time",
        action="store",
        help="Time to pause the scan at (format: YYYY-MM-DD HH:MM)",
        type=str,
    )
    optional_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    return parser