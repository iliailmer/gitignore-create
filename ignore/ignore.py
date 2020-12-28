import argparse
import os
from ignore.make_request import make_request

URL = "https://www.toptal.com/developers/gitignore/api/list?format=json"


def main() -> None:

    parser = argparse.ArgumentParser("IGNORE: A .gitignore generator tool.")

    parser.add_argument("-n", "--name", type=str, help="Language name")
    parser.add_argument(
        "-p", "--path", type=str, help="Output path", default="./"
    )
    resp = make_request()
    args = parser.parse_args()

    with open(f"{os.path.join(args.path, '.gitignore')}", "w") as f:
        f.write(resp.json()["python"]["contents"])


if __name__ == "__main__":
    main()
