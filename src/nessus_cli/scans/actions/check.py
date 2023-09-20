from argparse import ArgumentParser, _SubParsersAction
def check_action_args(parser: _SubParsersAction, std_parser: ArgumentParser) -> _SubParsersAction:
    """
    Add arguments for the check action to a _SubParsersAction[ArgumentParser]
    
    Args:
        parser (_SubParsersAction[ArgumentParser]): The subparser object
        std_parser (argparse.ArgumentParser): The standard parser object
        
    Returns:
        _SubParsersAction[ArgumentParser]: The parsed arguments
    """
    check_parser = parser.add_parser("check", help="Check the status of a scan", parents=[std_parser])
    
    required_groug = check_parser.add_argument_group("Required", "Required arguments")
    required_groug.add_argument(
        "-s",
        "--scan_id",
        action="store",
        help="Scan ID to check",
        type=int,
        required=True,
    )
    
    optional_group = check_parser.add_argument_group("Optional", "Optional arguments")
    optional_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    return parser