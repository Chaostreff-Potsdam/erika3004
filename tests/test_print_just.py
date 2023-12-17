#! /usr/bin/python3
from erika.erika import JustifiedErika
from sys import stdin
import time

e = JustifiedErika("/dev/ttyAMA0")

par = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
ut aliquip ex ea commodo consequat.""".replace("  ", " ").replace("  ", " ")

with e:
    for line in par.split("\n"):
        e.print_stretched_line(line, 60)
        e.print_string("\n")
        e.connection.flush()
        time.sleep(1)
