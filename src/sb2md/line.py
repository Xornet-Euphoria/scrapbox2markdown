from enum import Enum, auto
from typing import Union


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
        self.__hierarchy = None
        self.__block_status = BlockStatus.UNSET
        self.__header_level = -1

    # getters
    @property
    def text(self) -> str:
        return self.__text

    @property
    def hierarchy(self) -> Union[int, None]:
        return self.__hierarchy

    @property
    def block_status(self) -> BlockStatus:
        return self.__block_status

    @property
    def get_is_first(self) -> bool:
        return self.__is_first

    # setters
    @block_status.setter
    def block_status(self, type: BlockStatus):
        self.__block_status = type

    def set_header(self, level: int):
        if level < 1:
            raise ValueError("`level` must be positive number")

        self.__text = "#"*level + " " + self.__text
        self.__header_level = level

    def parse_and_set_header(self, max_header_level):
        if self.block_status != BlockStatus.NOTIN or len(self.__text) < 5:
            return

        if self.__text[0] != "[" or self.__text[1] != "*" or self.__text[-1] != "]":
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
