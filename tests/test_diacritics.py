#! /usr/bin/python3
from erika.erika import Erika
from sys import stdin
import time
e = Erika("/dev/ttyAMA0")
with e:
		e.print_string("^`´¨°²³")
		e.connection.flush()
		time.sleep(1)
