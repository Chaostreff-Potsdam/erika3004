from enum import Enum

ascii2erika = {
    # control chars
    "\b": b"\x72",
    "\t": b"\x79",
    "\n": b"\x77",
    "\r": b"\x78",

    # punctuation
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

    # digits
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

    # more punctuation
    ":": b"\x13",
    ";": b"\x3B",
    "=": b"\x2E",
    "?": b"\x35",

    # upper case letters
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

    # punctuation
    "^": b"\x19\x71",
    "_": b"\x01",
    "`": b"\x2B\x71",

    # lower case letters
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

    # special chars
    "|": b"\x27",
    "£": b"\x06",
    "§": b"\x3D",
    "¨": b"\x03\x71",
    "°": b"\x39",
    "²": b"\x15",
    "³": b"\x23",

    # umlauts, accents
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

    # combined chars
    "€": b"\x20\x72\x2E",
}

combined_chars = [
    "^",
    "`",
    "¨",
    "´",
    "€"
]

combining_diacritics = {
    "\u0300": b"\x2B",
    '\u0301': b"\x29",
    "\u0302": b"\x19",
    "\u0308": b"\x03",
    "\u030a": b"\x39"
}


class Direction:
    RIGHT = b"\x73"
    LEFT = b"\x74"
    UP = b"\x76"
    DOWN = b"\x75"



LINE_FEED = b"\x9F"


class MicroStep:
    LEFT_RIGHT = b"\xA5"
    UP = b"\x82"
    DOWN = b"\x81"

