from argparse import ArgumentParser, _SubParsersAction
def export_action_args(parser: _SubParsersAction, std_parser: ArgumentParser) -> _SubParsersAction:
    """
    Add arguments for the export action to a _SubParsersAction[ArgumentParser]
    
    Args:
        parser (_SubParsersAction[ArgumentParser]): The subparser object
        std_parser (argparse.ArgumentParser): The standard parser object
        
    Returns:
        _SubParsersAction[ArgumentParser]: The parsed arguments
    """
    export_parser = parser.add_parser("export", help="Export scan results", parents=[std_parser])
    
    required_groug = export_parser.add_argument_group("Required", "Required arguments")
    required_groug.add_argument(
        "-s",
        "--scan_id",
        action="store",
        help="Scan ID to export",
        type=int,
        required=True,
    )
    # TODO: Add support for more formats
    required_groug.add_argument(
        "-f",
        "--format",
        action="store",
        help="Format to export the scan results in",
        choices=["nessus", "html", "both"],
        type=str,
        required=True,
    )
    
    optional_group = export_parser.add_argument_group("Optional", "Optional arguments")
    optional_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    
    return parser