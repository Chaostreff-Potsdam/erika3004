import codecs
import sys
from typing import Tuple
import unicodedata

from erika.char_map import ascii2erika, combining_diacritics


def transpose_dict(dictionary):
    return {int.from_bytes(value, sys.byteorder): key for key, value in dictionary.items()}


def iter_good(data):
    index = 0
    peek_index = index + 1
    while index < len(data) and peek_index < len(data):
        peek_index = index + 1
        while peek_index < len(data):
            if not unicodedata.combining(data[peek_index]):
                yield data[index:peek_index]
                index = peek_index
                break
            else:
                peek_index += 1
    yield data[index:]


erika2ascii = transpose_dict(ascii2erika)


def get_composed_char(char: str):
    char, *combining_chars = unicodedata.normalize("NFD", char)
    return b"".join(combining_diacritics[c] for c in combining_chars) + ascii2erika[char]


def is_composed_char(char: str):
    return len(unicodedata.normalize("NFD", char)) > 1


def encode_char(char: str):
    # erika directly supports some composed chars
    if is_composed_char(char) and char not in ascii2erika.keys():
        return get_composed_char(char)
    else:
        return ascii2erika[char]


def encode(text: str, error: str = "strict") -> Tuple[bytes, int]:
    text = unicodedata.normalize("NFC", text)

    if error == "strict":
        return b"".join(encode_char(x) for x in iter_good(text)), len(text)
    elif error == "ignore":
        return b"".join(ascii2erika.get(x, ascii2erika[" "]) for x in iter_good(text)), len(text)
    else:
        raise Exception("invalid error handler")


def decode(binary: bytes, error: str = "strict") -> Tuple[str, int]:
    return "".join(erika2ascii[x] for x in binary), len(binary)


def search_function(encoding_name):
    return codecs.CodecInfo(encode, decode, name='DDRSCII')


codecs.register(search_function)
