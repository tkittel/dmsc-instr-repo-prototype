import argparse
from pathlib import Path

MODES = ["check", "runci", "list"]
DEFAULT_MODE = "list"

assert DEFAULT_MODE in MODES


def parse_args(argv=None,prog=None):
    if argv is None:
        import sys
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog=prog)

    parser.add_argument(
        "project_dir",
        help='Path to a directory containing a "project".',
    )

    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        choices=MODES,
        default=DEFAULT_MODE,
        help=f'Mode: {MODES} (default: "{DEFAULT_MODE}").',
    )

    args = parser.parse_args(argv)
    args.project_dir = Path(args.project_dir)
    return args

def main( argv = None ):
    args = parse_args(argv)
    from .analyse import analyse_dir
    info = analyse_dir( args.project_dir )
    import pprint
    pprint.pp(info)

    #print(f"project_dir={args.project_dir} mode={args.mode}")
    return 0


if __name__ == "__main__":
    main()
