import argparse


class CliParser:

    def __init__(self, prog_name: str):
        self.arg_parser = argparse.ArgumentParser(
            prog=prog_name,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.arg_parser.add_argument(
            '-i', '--interval', nargs=1,
            default='30', type=int
        )

    def get_interval(self) -> int:
        """
        Parse command line arguments
        :return: value for time interval
        """
        args = self.arg_parser.parse_args()
        return args.interval[-1]
