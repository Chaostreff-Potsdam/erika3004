#!/usr/bin/env python3

import socket
import string
import time

from erika.erika import Erika
from erika.local_settings import ERIKA_MAX_LINE_LENGTH
from erika.local_settings import ERIKA_PORT
from erika.local_settings import TCP_IP, TCP_PORT, BUFFER_SIZE

ALLOWED_CHARACTERS = string.digits + string.ascii_letters + "@.,;:# ()_/?!\"§+%&=*-'äöüÄÖÜßéè°|$£µ^²³\n"


# TODO bad style, use "with" statement instead for clean closing...
erika = Erika(ERIKA_PORT)
erika.set_keyboard_echo(False)

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


def print_to_erika(sanitized_tweet):
    erika.crlf()

    xpos = 0
    just_overflow = False
    for c in sanitized_tweet:
        xpos += 1

        if c == '\n':
            xpos = 0
            if just_overflow:
                just_overflow = False
                continue

        just_overflow = False
        erika.print_ascii(c)

        if xpos >= ERIKA_MAX_LINE_LENGTH:
            erika.crlf()
            xpos = 0
            just_overflow = True



while True:
    conn, addr = s.accept()
    print('Connection address:', addr)
    data = conn.recv(BUFFER_SIZE)

    try:
        sanitized_tweet = data.decode('utf-8')
        sanitized_tweet = ''.join(c for c in sanitized_tweet if c in ALLOWED_CHARACTERS)
        sanitized_tweet = sanitized_tweet.replace('@', "(at)")
        sanitized_tweet = '({}) Message sent by {}:{}:\n{}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), addr[0], addr[1], sanitized_tweet)

        print("sanitized data:", sanitized_tweet)
        print_to_erika(sanitized_tweet)
        # return sanitized data
        conn.send(sanitized_tweet.encode('utf-8'))
    except UnicodeDecodeError as e:
        conn.send("Invalid bytes. You must send UTF-8.\n".encode("utf-8"))
        print("Invalid bytes", e)
    except ConnectionError as e:
        print("Connection error", e)
    finally:
        conn.close()
