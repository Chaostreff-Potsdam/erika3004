import codecs
from typing import Tuple

ascii2erika = {
    "_": b"\x01",
    "&": b"\x02",
    "¨": b"\x03",
    "%": b"\x04",
    "i": b"\x05",
    "£": b"\x06",
    "μ": b"\x07",
    "9": b"\x08",
    "8": b"\x09",
    "7": b"\x0A",
    "6": b"\x0B",
    "5": b"\x0C",
    "0": b"\x0D",
    "4": b"\x0E",
    "3": b"\x0F",
    "2": b"\x10",
    "1": b"\x11",
    "H": b"\x12",
    ":": b"\x13",
    "D": b"\x14",
    "²": b"\x15",
    "M": b"\x16",
    "'": b"\x17",
    "B": b"\x18",
    "^": b"\x19",
    "Q": b"\x1A",
    "*": b"\x1B",
    "G": b"\x1C",
    "(": b"\x1D",
    "O": b"\x1E",
    ")": b"\x1F",
    "C": b"\x20",
    "I": b"\x21",
    "V": b"\x22",
    "³": b"\x23",
    "K": b"\x24",
    "+": b"\x25",
    "X": b"\x26",
    "|": b"\x27",
    "U": b"\x28",
    '́ ': b"\x29",
    "N": b"\x2A",
    "`": b"\x2B",
    "L": b"\x2C",
    "W": b"\x2D",
    "=": b"\x2E",
    "P": b"\x2F",
    "A": b"\x30",
    "Y": b"\x31",
    "J": b"\x32",
    "S": b"\x33",
    "E": b"\x34",
    "?": b"\x35",
    "R": b"\x36",
    "T": b"\x37",
    "Z": b"\x38",
    "°": b"\x39",
    "Ü": b"\x3A",
    ";": b"\x3B",
    "Ö": b"\x3C",
    "§": b"\x3D",
    "F": b"\x3E",
    "Ä": b"\x3F",
    "/": b"\x40",
    "#": b"\x41",
    "!": b"\x42",
    '"': b"\x43",
    "é": b"\x44",
    "ç": b"\x45",
    "è": b"\x46",
    "ß": b"\x47",
    "$": b"\x48",
    "f": b"\x49",
    "m": b"\x4A",
    "j": b"\x4B",
    "w": b"\x4C",
    "l": b"\x4D",
    "b": b"\x4E",
    "v": b"\x4F",
    "k": b"\x50",
    "y": b"\x51",
    "q": b"\x52",
    "d": b"\x53",
    "z": b"\x54",
    "h": b"\x55",
    "t": b"\x56",
    "c": b"\x57",
    "s": b"\x58",
    "r": b"\x59",
    "e": b"\x5A",
    "p": b"\x5B",
    "n": b"\x5C",
    "u": b"\x5D",
    "o": b"\x5E",
    "x": b"\x5F",
    "g": b"\x60",
    "a": b"\x61",
    "-": b"\x62",
    ".": b"\x63",
    ",": b"\x64",
    "ä": b"\x65",
    "ö": b"\x66",
    "ü": b"\x67",
    " ": b"\x71",
    "\b": b"\x72",
    "\r": b"\x78",
    "\t": b"\x79",
    "\n": b"\x77",
}


def transpose_dict(dictionary):
    return {value: key for key, value in dictionary.items()}


erika2ascii = transpose_dict(ascii2erika)


def encode(text: str, error: str = "strict") -> Tuple[bytes, int]:
    if error == "strict":
        return b"".join(ascii2erika[x] for x in text), len(text)
    elif error == "ignore":
        return b"".join(ascii2erika.get(x, ascii2erika[" "]) for x in text), len(text)
    else:
        raise Exception("invalid error handler")


def decode(binary: bytes, error: str = "strict") -> Tuple[str, int]:
    return "".join(erika2ascii[x] for x in binary), len(binary)


def search_function(encoding_name):
    return codecs.CodecInfo(encode, decode, name='DDRSCII')


codecs.register(search_function)
