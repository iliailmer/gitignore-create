import argparse
import os
import sys
from ignore.utils import get_file, get_template_list, search_templates, validate_gitignore_response


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
            # get_template_list() returns sorted results
            templates = get_template_list()
            for template in templates:
                print(template)
            return
        except RuntimeError as e:
            print(f"Error fetching template list: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    # Handle --search
    if args.search:
        try:
            # search_templates() returns sorted results
            results = search_templates(args.search)
            if results:
                for template in results:
                    print(template)
            else:
                print(f"No templates found matching '{args.search}'")
            return
        except RuntimeError as e:
            print(f"Error searching templates: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    # If no names provided and not using --list or --search, launch TUI
    if not args.names:
        from ignore.tui import GitignoreTUI
        app = GitignoreTUI()
        app.run()
        return

    # Fetch template content
    try:
        content = get_file(args.names)

        # Check for errors in response
        if not validate_gitignore_response(content):
            print("Something went wrong, language not found!", file=sys.stderr)
            sys.exit(1)

        # Handle --preview mode
        if args.preview:
            print(content)
            if args.append:
                # Treat append text as-is, preserving any formatting
                print("\n" + args.append.strip())
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
                # Treat append text as-is, preserving any formatting
                f.write("\n" + args.append.strip())
        else:
            # Normal write mode
            with open(gitignore_path, "w") as f:
                f.write(content)

        print("Success!")

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
