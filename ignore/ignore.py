import argparse
import os
import sys
from ignore.utils import get_file, get_template_list, search_templates


def main() -> None:
    parser = argparse.ArgumentParser("IGNORE: A .gitignore generator tool.")

    parser.add_argument(
        "-n",
        "--names",
        required=False,
        nargs="+",
        help="Language name(s); pass as many names as necessary.",
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        type=str,
        help="Output path; where to save the '.gitignore' file",
        default="./",
    )
    parser.add_argument(
        "-a",
        "--append",
        required=False,
        help="Append custom text to the current or new gitignore file",
        default="",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available templates",
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        help="Search for templates matching the given term",
    )
    parser.add_argument(
        "-d",
        "--preview",
        action="store_true",
        help="Dry-run mode; print to stdout instead of writing to file",
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        try:
            templates = get_template_list()
            templates.sort()
            for template in templates:
                print(template)
            return
        except Exception as e:
            print(f"Error fetching template list: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle --search
    if args.search:
        try:
            results = search_templates(args.search)
            results.sort()
            if results:
                for template in results:
                    print(template)
            else:
                print(f"No templates found matching '{args.search}'")
            return
        except Exception as e:
            print(f"Error searching templates: {e}", file=sys.stderr)
            sys.exit(1)

    # If no names provided and not using --list or --search, launch TUI
    if not args.names:
        from ignore.tui import GitignoreTUI
        app = GitignoreTUI()
        app.run()
        return

    # Fetch template content
    try:
        resp = get_file(args.names)
        content = resp.content.decode("utf-8")

        # Check for errors in response
        if "error" in content.lower():
            print("Something went wrong, language not found!", file=sys.stderr)
            sys.exit(1)

        # Handle --preview mode
        if args.preview:
            print(content)
            if args.append:
                text_to_append = args.append.strip().split(" ")
                print("\n".join(text_to_append))
            return

        # Write to file
        gitignore_path = os.path.join(args.path, '.gitignore')

        # Handle append mode
        if args.append:
            # Read existing content if file exists
            existing_content = ""
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r") as f:
                    existing_content = f.read()

            # Write everything back
            with open(gitignore_path, "w") as f:
                if existing_content:
                    f.write(existing_content)
                    if not existing_content.endswith("\n"):
                        f.write("\n")
                f.write(content)
                text_to_append = args.append.strip().split(" ")
                f.write("\n" + "\n".join(text_to_append))
        else:
            # Normal write mode
            with open(gitignore_path, "w") as f:
                f.write(content)

        print("Success!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
