import os
import argparse
import shutil
import datetime
import pwd
import time
import prettytable


TRASH_PATH = ".trash"
SCRIPT_NAME = "Trashify"


def move_to_trash(
    files: list[str],
    verbose: bool = False,
    recursive: bool = False,
    dir: bool = False,
    force: bool = False,
):
    if not os.path.exists(TRASH_PATH):
        os.makedirs(TRASH_PATH)
    for filepath in files:
        if not os.path.exists(filepath):
            if not force:
                print(
                    f"{SCRIPT_NAME}: cannot remove '{filepath}': No such file or directory"
                )
            continue
        if os.path.isdir(filepath):
            dir_files = os.listdir(filepath)
            if not len(dir_files) and not dir and not recursive:
                if not force:
                    print(f"{SCRIPT_NAME}: cannot remove '{filepath}': Is a directory")
                continue

        src = os.path.basename(filepath)
        timestamp = time.time()
        dst = os.path.join(TRASH_PATH, f"{timestamp}-{src}")
        shutil.move(src, dst)
        if verbose:
            print(f"removed '{filepath}'")


def get_trash_content():
    trash_listdir = sorted(os.listdir(TRASH_PATH))

    trash_content = {}

    for content in trash_listdir:
        filepath = os.path.join(TRASH_PATH, content)
        stats = os.stat(filepath)
        is_dir = os.path.isdir(filepath)

        trash_content[content] = {
            "id": None,
            "type": "Dir" if is_dir else "File",
            "owner": pwd.getpwuid(stats.st_uid).pw_name,
            "size": stats.st_size,
            "st_mtime": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)
            ),
        }
    for idx, (_, value) in enumerate(trash_content.items(), start=1):
        value["id"] = idx

    return trash_content


def list_trash_content():
    trash_content = get_trash_content()

    if not trash_content:
        print("Trash is empty")
        return

    table = prettytable.PrettyTable()

    table.field_names = [
        "ID",
        "Date Moved",
        "Type",
        "Name",
        "Size (bytes)",
        "Owner",
        "Last Modified",
    ]

    for name, data in trash_content.items():
        try:
            copy_date, filename = name.split("-", 1)
            copy_date = float(copy_date)
            str_date_moved = datetime.datetime.fromtimestamp(copy_date).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            str_date_moved = "Unknown"
            filename = name

        table.add_row(
            [
                data["id"],
                str_date_moved,
                data["type"],
                filename,
                data["size"],
                data["owner"],
                data["st_mtime"],
            ]
        )

    print(table)


def clear_trash():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description=f"{SCRIPT_NAME} - A safe replacement for rm.",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=f"{SCRIPT_NAME} directories and their contents recursively.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Explain what is being done."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Ignore nonexistent files and arguments, never prompt.",
    )

    parser.add_argument(
        "-d", "--dir", action="store_true", help="remove empty directories"
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List the contents of the trash directory.",
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Files or directories to remove. Optional when using --list.",
    )

    args = parser.parse_args()

    if args.list:
        if args.files:
            parser.error(f"{SCRIPT_NAME}: --list does not accept files.")
        list_trash_content()

    else:
        if not args.files:
            parser.error(f"{SCRIPT_NAME}: the following arguments are required: files")
        move_to_trash(
            files=args.files,
            verbose=args.verbose,
            recursive=args.recursive,
            dir=args.dir,
            force=args.force,
        )
