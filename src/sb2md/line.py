from enum import Enum, auto
from typing import Dict, Union
import re
import typing


class BlockStatus(Enum):
    NOTIN = auto(),
    BLOCKSTART = auto(),
    BLOCKEND = auto(),
    INBLOCK = auto()
    UNSET = auto()


class Line:
    def __init__(self, text: str, is_first: bool=False):
        self.__is_first = is_first
        self.__original_text = text  # don't change
        self.__text = text
        self.__hierarchy = -1
        self.type = None
        self.block_status = BlockStatus.UNSET

    # getters
    @property
    def text(self) -> str:
        return self.__text

    @property
    def hierarchy(self) -> int:
        return self.__hierarchy

    @property
    def get_is_first(self) -> bool:
        return self.__is_first

    # for table and code block in list
    # These layout is dirty so they are disabled. 
    def strip_for_block_start(self):
        self.__text = self.__text.strip()

    def set_header(self, level: int):
        if level < 1:
            raise ValueError("`level` must be positive number")

        self.__text = "#"*level + " " + self.__text


    def parse_and_set_header(self, max_header_level):
        if self.type != "header":
            return

        pos = 1
        while True:
            pos += 1
            if self.__text[pos] != "*":
                break
        star_cnt = pos - 1
        self.__text = self.__text[pos+1:-1]

        if star_cnt > max_header_level:
            self.set_header(2)
        else:
            self.set_header(max_header_level - star_cnt + 2)


    def __calculate_hierarchy(self):
        if self.type == "list":
            self.__text = self.__text[1:]
        pos = 0
        while True:
            if self.__text[pos] != " " and self.__text[pos] != "\t":
                break
            pos += 1

        self.__hierarchy = pos

    def __insert_space(self):
        if self.__hierarchy < 0:
            raise ValueError("list hierarchy must be larger than or equal to 0")
        prefix = "- " if self.type == "list" else ""
        self.__text = self.__text.lstrip()
        self.__text = "  " * self.__hierarchy + prefix + self.__text


    def make_list(self):
        if self.type != "list" and self.type != "numlist":
            return
        self.__calculate_hierarchy()
        self.__insert_space()


    def determine_type(self, patterns: typing.Dict[str, typing.Dict]):
        if self.block_status != BlockStatus.NOTIN:
            return

        for linetype, pattern in patterns.items():
            res = pattern.match(self.__text)
            if res:
                self.type = linetype


    def make_codeblock(self):
        if self.block_status == BlockStatus.BLOCKSTART:
            codename = self.__text[5:]
            self.__text = "```" + codename
        elif self.block_status == BlockStatus.INBLOCK:
            # eliminate 1st space
            self.__text = self.__text[1:]
        elif self.block_status == BlockStatus.BLOCKEND:
            self.__text = "```\n" + self.__text


    def make_table(self):
        if self.block_status == BlockStatus.BLOCKSTART:
            self.__text = ""
        elif self.block_status == BlockStatus.INBLOCK:
            self.__text = self.__text.replace(" ", "")
            self.__text = self.__text.replace("\t", "|")
            self.__text = f"|{self.__text}|"
        elif self.block_status == BlockStatus.BLOCKEND:
            self.__text = ""
