import argparse
import os
from ignore.utils import get_file

# TODO: requests as a requirement


def main() -> None:

    parser = argparse.ArgumentParser("IGNORE: A .gitignore generator tool.")

    parser.add_argument(
        "-n",
        "--names",
        required=True,
        nargs="+",
        help=("Language name(s); pass as many names as necessary."),
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        type=str,
        help="Output path; where to save the '.gitignore' file",
        default="./",
    )
    args = parser.parse_args()

    resp = get_file(args.names)
    with open(f"{os.path.join(args.path, '.gitignore')}", "w") as f:
        content = resp.content.decode("utf-8")
        if "error" in content.lower():
            print("Something went wrong, language not found!")
        else:
            f.write(content)
            print("Success!")


if __name__ == "__main__":
    main()
