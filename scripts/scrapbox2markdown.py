from typing import List
from sb2md.connect import get_text, APIConnectionError
from argparse import ArgumentParser

from sb2md.parse import Parser


def get_args() -> List:
    parser = ArgumentParser()
    parser.add_argument("project", help="project name")
    parser.add_argument("title", help="article title")
    parser.add_argument("--sid", help="If project is private, please specify sid here.")
    parser.add_argument("-o", "--out", help="If specified, markdown file is created. If not, result is written to stdout.")
    parser.add_argument("--max-header", help="header level of scrapbox that converted to h2", default=4, type=int)
    return parser.parse_args()



def main() -> None:
    args = get_args()
    project = args.project
    title = args.title

    is_private = False
    sid = args.sid
    if sid is not None:
        is_private = True
    max_header_level = args.max_header

    try:
        text = get_text(project, title, is_private, sid)
        parser = Parser(text, max_header_level=max_header_level)
        parser.parse_lines()
        res = parser.get_md_text()
        print(res)
        # debug
        # lines = parser.get_lines()
        # for line in lines:
            # print(f"[{line.type}]{line.text}")
    except APIConnectionError as err:
        print("[ERROR]: Connection Error Occured.")
        print(f"{err}")
        exit(1)
    except Exception as err:
        print("[ERROR]: Unexpected Error")
        print(f"{err}")
        raise err


if __name__ == "__main__":
    main()
