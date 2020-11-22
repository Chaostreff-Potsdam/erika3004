import codecs
from typing import Tuple
import unicodedata

ascii2erika = {
    "\b": b"\x72",
    "\t": b"\x79",
    "\n": b"\x77",
    "\r": b"\x78",

    " ": b"\x71",
    "!": b"\x42",
    '"': b"\x43",
    "#": b"\x41",
    "$": b"\x48",
    "%": b"\x04",
    "&": b"\x02",
    "'": b"\x17",
    "(": b"\x1D",
    ")": b"\x1F",
    "*": b"\x1B",
    "+": b"\x25",
    ",": b"\x64",
    "-": b"\x62",
    ".": b"\x63",
    "/": b"\x40",

    "0": b"\x0D",
    "1": b"\x11",
    "2": b"\x10",
    "3": b"\x0F",
    "4": b"\x0E",
    "5": b"\x0C",
    "6": b"\x0B",
    "7": b"\x0A",
    "8": b"\x09",
    "9": b"\x08",

    ":": b"\x13",
    ";": b"\x3B",
    "=": b"\x2E",
    "?": b"\x35",

    "A": b"\x30",
    "B": b"\x18",
    "C": b"\x20",
    "D": b"\x14",
    "E": b"\x34",
    "F": b"\x3E",
    "G": b"\x1C",
    "H": b"\x12",
    "I": b"\x21",
    "J": b"\x32",
    "K": b"\x24",
    "L": b"\x2C",
    "M": b"\x16",
    "N": b"\x2A",
    "O": b"\x1E",
    "P": b"\x2F",
    "Q": b"\x1A",
    "R": b"\x36",
    "S": b"\x33",
    "T": b"\x37",
    "U": b"\x28",
    "V": b"\x22",
    "W": b"\x2D",
    "X": b"\x26",
    "Y": b"\x31",
    "Z": b"\x38",

    "^": b"\x19\x71",
    "_": b"\x01",
    "`": b"\x2B\x71",

    "a": b"\x61",
    "b": b"\x4E",
    "c": b"\x57",
    "d": b"\x53",
    "e": b"\x5A",
    "f": b"\x49",
    "g": b"\x60",
    "h": b"\x55",
    "i": b"\x05",
    "j": b"\x4B",
    "k": b"\x50",
    "l": b"\x4D",
    "m": b"\x4A",
    "n": b"\x5C",
    "o": b"\x5E",
    "p": b"\x5B",
    "q": b"\x52",
    "r": b"\x59",
    "s": b"\x58",
    "t": b"\x56",
    "u": b"\x5D",
    "v": b"\x4F",
    "w": b"\x4C",
    "x": b"\x5F",
    "y": b"\x51",
    "z": b"\x54",


    "|": b"\x27",
    "£": b"\x06",
    "§": b"\x3D",
    "¨": b"\x03\x71",
    "°": b"\x39",
    "²": b"\x15",
    "³": b"\x23",

    "Ä": b"\x3F",
    "Ö": b"\x3C",
    "Ü": b"\x3A",
    "ß": b"\x47",
    "ä": b"\x65",
    "ç": b"\x45",
    "è": b"\x46",
    "é": b"\x44",
    "ö": b"\x66",
    "ü": b"\x67",
    "´": b"\x29\x71",
    "μ": b"\x07",
}
combining_diacritics={
    "\u0300": b"\x2B",
    '\u0301': b"\x29",
    "\u0302": b"\x19",
    "\u0308": b"\x03",
    "\u030a": b"\x39"
}


def transpose_dict(dictionary):
    return {value: key for key, value in dictionary.items()}


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
        return b"".join(encode_char(x) for x in text), len(text)
    elif error == "ignore":
        return b"".join(ascii2erika.get(x, ascii2erika[" "]) for x in text), len(text)
    else:
        raise Exception("invalid error handler")


def decode(binary: bytes, error: str = "strict") -> Tuple[str, int]:
    return "".join(erika2ascii[x] for x in binary), len(binary)


def search_function(encoding_name):
    return codecs.CodecInfo(encode, decode, name='DDRSCII')


codecs.register(search_function)
