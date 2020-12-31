from typing import List, Union
from sb2md.line import Line, BlockStatus
import typing


start_block_elms = ["table:", "code:"]


def get_block_type(text: str) -> Union[str, None]:
    for block_elm in start_block_elms:
        if text[0:len(block_elm)] == block_elm:
            return block_elm

    return None


def parse_block_structure(lines: typing.List[Line]) -> None:
    first_line = lines[0]
    first_line.block_status = BlockStatus.NOTIN
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
                in_block = True
                line.block_status = BlockStatus.BLOCKSTART
            else:
                line.block_status = BlockStatus.NOTIN


def init_lines(raw_lines: typing.List[str]) -> typing.List[Line]:
    lines = [Line(raw_lines[0], is_first=True)]
    for raw_line in raw_lines[1:]:
        lines.append(Line(raw_line))

    return lines


def parse_header(lines: typing.List[Line], max_header_level) -> None:
    first_line = lines[0]
    first_line.set_header(1)
    in_block = False
    for line in lines[1:]:
        line.parse_and_set_header(max_header_level)


def parse_text(text: str, max_header_level: int) -> List:
    raw_lines = text.split("\n")
    lines = init_lines(raw_lines)
    parse_block_structure(lines)
    parse_header(lines, max_header_level)

    return lines