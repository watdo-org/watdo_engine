from typing import TypedDict


class PartialBlockData(TypedDict, total=False):
    pass


class BlockData(PartialBlockData):
    pass


def parse_code(code: str) -> BlockData:
    raise NotImplementedError
