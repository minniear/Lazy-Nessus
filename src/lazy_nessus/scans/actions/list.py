from argparse import ArgumentParser, _SubParsersAction
def list_action_args(parser: _SubParsersAction, std_parser: ArgumentParser) -> _SubParsersAction:
    """
    Add arguments for the list action to a _SubParsersAction[ArgumentParser]
    
    Args:
        parser (_SubParsersAction[ArgumentParser]): The subparser object
        std_parser (argparse.ArgumentParser): The standard parser object
        
    Returns:
        _SubParsersAction[ArgumentParser]: The parsed arguments
    """
    list_parser = parser.add_parser("list", help="List all scans", parents=[std_parser])
    
    optional_group = list_parser.add_argument_group("Optional", "Optional arguments")
    optional_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    return parser