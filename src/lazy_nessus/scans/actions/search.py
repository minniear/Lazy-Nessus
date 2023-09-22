from argparse import ArgumentParser, _SubParsersAction
def search_action_args(parser: _SubParsersAction, std_parser: ArgumentParser) -> _SubParsersAction:
    """
    Add arguments for the search action to a _SubParsersAction[ArgumentParser]
    
    Args:
        parser (_SubParsersAction[ArgumentParser]): The subparser object
        std_parser (argparse.ArgumentParser): The standard parser object
        
    Returns:
        _SubParsersAction[ArgumentParser]: The parsed arguments
    """
    search_parser = parser.add_parser("search", help="search for scans", parents=[std_parser])
    
    optional_group = search_parser.add_argument_group("Optional", "Optional arguments")
    optional_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    required_group = search_parser.add_argument_group("Required", "Required arguments")
    required_group.add_argument(
        "-s",
        "--search-string",
        action="store",
        help="Search string",
        type=str,
        required=True,
    )
    
    return parser