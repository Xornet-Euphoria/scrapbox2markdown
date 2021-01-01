from typing import List, Union
from sb2md.line import Line, BlockStatus
import typing
import re


class Parser:
    def __init__(self, text: str, max_header_level: int=4) -> None:
        raw_lines = text.split("\n")
        self.__lines = [Line(raw_lines[0], is_first=True)]
        for raw_line in raw_lines[1:]:
            self.__lines.append(Line(raw_line))
        self.__max_header_level = max_header_level

    def parse_lines(self):
        self.process_first_line()
        self.parse_block_structure()
        self.set_line_type()
        self.parse_header(self.__max_header_level)
        self.parse_list()
        self.parse_code_block()
        self.parse_table()

    def process_first_line(self) -> None:
        first_line = self.__lines[0]
        first_line.block_status = BlockStatus.NOTIN
        first_line.set_header(1)
        first_line.type = "title"


    def get_block_type(self, text: str) -> Union[str, None]:
        start_block_elms = ["table:", "code:"]

        for block_elm in start_block_elms:
            if text[0:len(block_elm)] == block_elm:
                return block_elm

        return None

    def parse_block_structure(self) -> None:
        in_block = False
        for line in self.__lines[1:]:
            if in_block:
                if len(line.text) == 0 or line.text[0] != " ":
                    line.block_status = BlockStatus.BLOCKEND
                    in_block = False
                else:
                    line.block_status = BlockStatus.INBLOCK
            else:
                block_type = self.get_block_type(line.text.strip())
                if block_type is not None:
                    line.strip_for_block_start()
                    in_block = True
                    line.block_status = BlockStatus.BLOCKSTART
                    line.type = block_type[:-1]
                else:
                    line.block_status = BlockStatus.NOTIN

    def set_line_type(self) -> None:
        patterns = {
            "header": re.compile(r"^\[\*+\s.*]"),
            "quote": re.compile(r"^\>.*"),
            "list": re.compile(r"^(\t|\s)+.+"),
            "numlist": re.compile(r"^(\t|\s)*\d+\.\s.+"),
            "empty": re.compile(r"^(\t|\s)*$")
        }

        for line in self.__lines[1:]:
            line.determine_type(patterns)

    def parse_header(self, max_header_level) -> None:
        for i, line in enumerate(self.__lines[1:]):
            if line.type == "header":
                line.parse_and_set_header(max_header_level)

    def parse_list(self) -> None:
        for line in self.__lines:
            if line.type == "list" or line.type == "numlist":
                line.make_list()

    def parse_code_block(self) -> None:
        in_block = False
        for line in self.__lines:
            if line.block_status == BlockStatus.BLOCKSTART and line.type == "code":
                line.make_codeblock()
                in_block = True
            elif in_block and line.block_status == BlockStatus.INBLOCK:
                line.make_codeblock()
            elif in_block and line.block_status == BlockStatus.BLOCKEND:
                line.make_codeblock()
                in_block = False

    def parse_table(self) -> None:
        in_block = False
        for line in self.__lines:
            if line.block_status == BlockStatus.BLOCKSTART and line.type == "table":
                line.make_table()
                in_block = True
            elif in_block and line.block_status == BlockStatus.INBLOCK:
                line.make_table()
            elif in_block and line.block_status == BlockStatus.BLOCKEND:
                line.make_table()
                in_block = False

    def get_md_text(self):
        res = ""
        for line in self.__lines:
            res += line.text
            res += "\n"

        # eliminate last "\n"
        return res[:-1]

    # [debug]
    def get_lines(self):
        return self.__lines
