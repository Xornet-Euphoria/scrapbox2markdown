from typing import List, Union
from sb2md.line import Line, BlockStatus
import typing
import re


start_block_elms = ["table:", "code:"]


def get_block_type(text: str) -> Union[str, None]:
    for block_elm in start_block_elms:
        if text[0:len(block_elm)] == block_elm:
            return block_elm

    return None


def parse_block_structure(lines: typing.List[Line]) -> None:
    in_block = False
    for line in lines[1:]:
        if in_block:
            if line.text == "":
                line.block_status = BlockStatus.BLOCKEND
                in_block = False
            else:
                line.block_status = BlockStatus.INBLOCK
        else:
            block_type = get_block_type(line.text.strip())
            if block_type is not None:
                line.strip_for_block_start()
                in_block = True
                line.block_status = BlockStatus.BLOCKSTART
                line.type = block_type[:-1]
            else:
                line.block_status = BlockStatus.NOTIN


def set_line_type(lines: typing.List[Line]) -> None:
    patterns = {
        "header": re.compile(r"^\[\*+\s.*]"),
        "quote": re.compile(r"^\>.*"),
        "list": re.compile(r"^(\t|\s)+.+"),
        "numlist": re.compile(r"^(\t|\s)*\d+\.\s.+"),
        "empty": re.compile(r"^(\t|\s)*$")
    }
    for line in lines[1:]:
        line.determine_type(patterns)


def process_first_line(lines: typing.List[Line]) -> None:
    first_line = lines[0]
    first_line.block_status = BlockStatus.NOTIN
    first_line.set_header(1, add_newline=True)
    first_line.type = "title"


def init_lines(raw_lines: typing.List[str]) -> typing.List[Line]:
    lines = [Line(raw_lines[0], is_first=True)]
    for raw_line in raw_lines[1:]:
        lines.append(Line(raw_line))

    process_first_line(lines)

    return lines


def parse_header(lines: typing.List[Line], max_header_level) -> None:
    for i, line in enumerate(lines[1:]):
        if line.type == "header":
            add_newline = (i < len(lines) - 2 and lines[i+1].type != "empty")
            line.parse_and_set_header(max_header_level, add_newline)


def parse_list(lines: typing.List[Line]) -> None:
    for line in lines[1:]:
        if line.type == "list" or line.type == "numlist":
            line.make_list()


def parse_text(text: str, max_header_level: int) -> List:
    raw_lines = text.split("\n")
    lines = init_lines(raw_lines)
    parse_block_structure(lines)
    set_line_type(lines)
    parse_header(lines, max_header_level)
    parse_list(lines)

    return lines
