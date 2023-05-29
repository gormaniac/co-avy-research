""""Flatten" the objects found in certain dirs.

Operates on the files named ``##.json`` and flattens all objects within them.

Don't commit flattened field reports to git as the file is too big.
"""

import json
import sys

SUPPORTER_DIRS = {
    "classic_ids": "../data/classic_ids",
    "field_reports": "../data/field_reports",
}
YEARS = range(10, 24)

FileOrJsonError = (OSError, json.JSONDecodeError)


def get_years_json(path: str):
    """Yield the json from all files in path that are named for a year."""

    for year in iter(YEARS):
        try:
            with open(f"{path}/{year}.json", "r", encoding="utf-8") as fd:
                yield json.load(fd)
        except FileOrJsonError:
            continue

def main():
    """Main logic."""

    try:
        flatten_dir = sys.argv[1]
        if flatten_dir not in SUPPORTER_DIRS:
            raise IndexError
    except IndexError:
        print("Must pass a supported dir in data/ to flatten.")
        sys.exit(1)


    dir_path = SUPPORTER_DIRS.get(flatten_dir)

    match flatten_dir:
        case "classic_ids":
            flattened = {}
            for year_json in get_years_json(dir_path):
                flattened.update(year_json)
        case "field_reports":
            flattened = []
            for year_json in get_years_json(dir_path):
                for item in year_json:
                    flattened.append(item)

    try:
        with open(f"{dir_path}/flattened.json", "w", encoding="utf-8") as fd:
            json.dump(flattened, fd)
    except FileOrJsonError:
        print("Unable to write flattened object.")
        sys.exit(1)

if __name__ == "__main__":
    main()
